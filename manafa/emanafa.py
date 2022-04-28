import json
import sys
import time
from manafa.services.batteryStatsService import BatteryStatsService
from manafa.services.service import *
from manafa.services.perfettoService import PerfettoService
from manafa.parsing.perfetto.perfettoParser import PerfettoCPUfreqParser
from manafa.parsing.batteryStats.BatteryStatsParser import BatteryStatsParser
from manafa.utils.Logger import log, LogSeverity
from manafa.utils.Utils import execute_shell_command, mega_find, get_resources_dir, is_float

MANAFA_RESOURCES_DIR = get_resources_dir()

DEFAULT_PROFILE = os.path.join(MANAFA_RESOURCES_DIR, "profiles", "power_profile.xml")
DEFAULT_TIMEZONE = "GMT"


def get_last_boot_time(bts_file=None):
    """Retrieves timestamp of device last boot, either from the batterystats output filename that contains that info or
    the device itself.

    Args:
      bts_file(str): filename or filename, whose filename contains the boot time of the respective session where it was
      recorded.

    Returns:
      timestamp(float): secs.ms.
    """
    res, out, err = execute_shell_command(
        "adb shell cat /proc/stat | grep btime | awk '{print $2}'")  # executeShCommand("adb shell cat /proc/stat | grep btime | awk '{print $2}'")
    if res != 0 or len(out) == 0:
        log("no device connected. Assuming Boot time of battery stats file", LogSeverity.WARNING)
        flds = os.path.basename(bts_file).split("-") if bts_file is not None else []
        if len(flds) > 1:
            boot_time = flds[2].replace(".log", "")
            log("Boot time: " + boot_time, LogSeverity.WARNING)
            return int(float(boot_time))
        else:
            log("no device connected. Assuming Boot time 0", LogSeverity.WARNING)
            return 0
        # raise Exception("Invalid boot time ")
    # print("[Warning]: no device connected. Assuming Boot time %d" % boot_time)
    return float(out.strip())



class EManafa(Service):
    """Main class that abstracts all the modules and steps of the profiling procedure

    Attributes:
        resources_dir: directory where aux resources are contained
        power_profile: the power profile to be used in the profiling sessions
        boot_time: device's last boot timestamp
        batterystats: batterystats service
        perfetto: perfetto service
        timezone: device timezone
        unplugged: if the device is not charging
        bat_events: Batterystats parser
        pft_out_file: perfetto service output file
        bts_out_file: batterystats output file
    """
    def __init__(self, power_profile=None, timezone=None, resources_dir=MANAFA_RESOURCES_DIR):
        super(EManafa, self).__init__()
        self.resources_dir = resources_dir
        self.power_profile = power_profile if power_profile is not None else self.infer_power_profile()
        self.boot_time = 0
        log("Power profile file: " + self.power_profile, LogSeverity.INFO)
        self.batterystats = BatteryStatsService()
        self.perf_events = None
        self.perfetto = PerfettoService()
        self.timezone = timezone if timezone is not None else self.__infer_timezone()
        self.unplugged = False
        self.bat_events = None
        self.pft_out_file = None
        self.bts_out_file = None

    def config(self, **kwargs):
        pass

    def init(self):
        """inits inner services and virtually unplugs device if it is fully charged"""
        self.boot_time = get_last_boot_time()
        self.batterystats.init(boot_time=self.boot_time)
        self.perfetto.init(boot_time=self.boot_time)
        self.unplug_if_fully_charged()


    def start(self):
        """starts inner services."""
        self.batterystats.start()
        self.perfetto.start()


    def stop(self, run_id=None):
        """stops inner services.

        Returns:
            bts_file(str): path to the resultant batterystats log file.
            pf_out_file(str): path to the resultant perfetto log file.
        """
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        self.bts_out_file = self.batterystats.stop(run_id)
        self.pft_out_file = self.perfetto.stop(run_id)
        log("Perfetto file:  %s" % self.pft_out_file)
        self.parse_results(self.bts_out_file, self.pft_out_file)
        if self.unplugged:
            self.plug_back()
        return self.bts_out_file, self.pft_out_file


    def clean(self):
        """calls clean methods from inner services to clean previous result files."""
        self.batterystats.clean()
        self.perfetto.clean()

    def parse_results(self, bts_file=None, pf_file=None):
        """parses results from output results files of perfetto and batterystats services.
        Args:
            bts_file: batterystats output file. if none, uses self.bts_out_file
            pf_file: perfetto output file. if none, uses self.pft_out_file
        """
        if bts_file is None:
            bts_file = self.bts_out_file
        if pf_file is None:
            pf_file = self.pft_out_file
        if bts_file is None or pf_file is None:
            log("Empty result files",
                log_sev=LogSeverity.FATAL)
        self.boot_time = get_last_boot_time(bts_file)
        self.bat_events = BatteryStatsParser(self.power_profile, timezone=self.timezone)
        self.bat_events.parse_file(bts_file)
        self.perf_events = PerfettoCPUfreqParser(self.power_profile, self.boot_time, timezone=self.timezone)
        self.perf_events.parse_file(pf_file)

    def get_consumption_in_between(self, start_time=0, end_time=sys.maxsize):
        """retrieves energy consumption and device events between a timestamp interval.

        Args:
            start_time: begin timestamp.
            end_time: end timestamp.
        Returns:
            total(float): system-level energy consumption.
            per_component(dict): per-component energy consumption.
            metrics(dict): batterystats info containing events occurred during the interval. for each type of event, it
            presents.
        """
        total, per_component = self.calculate_non_cpu_energy(start_time, end_time)
        total_cpu = self.calculate_cpu_energy(start_time, end_time)
        metrics = self.bat_events.get_events_in_between(start_time, end_time)
        per_component['cpu'] += total_cpu
        return total + total_cpu, per_component, metrics

    def calculate_glob_and_component_consumption(self, last_event, per_component_consumption, delta_time, total):
        """ retrieves the global and per-component consumption of a state that lasts delta_time.
        Args:
            last_event: the event containing the last state.
            per_component_consumption: per_component consumption so far.
            delta_time: duration of the state.
            total: total consumption so far.

        Returns:
            total(float): total consumed (at device level).
            per_component_consumption(dict): consumption per device component.
        """
        tot_curr, comps_curr = last_event.get_current_of_batStatEvent()
        total += tot_curr * (last_event.get_voltage_value()) * delta_time
        for comp, comp_curr in comps_curr.items():
            if comp not in per_component_consumption:
                per_component_consumption[comp] = 0
            if is_float(comp_curr):
                per_component_consumption[comp] += (comp_curr * last_event.get_voltage_value() * delta_time)
        return total, per_component_consumption

    def calculate_non_cpu_energy(self, start_time, end_time):
        """Obtains energy consumption of device between a timestamp interval for every component except cpu. for cpu component,
        it stores only the state recorded in battarystats.
        Args:
            start_time: begin timestamp.
            end_time: end timestamp.

        Returns:
            total: system-level energy consumption without cpu energy consumption.
            per_component: per-component energy consumption without cpu energy consumption.

        """
        c_beg_bef, c_beg_aft = self.bat_events.get_closest_pair(start_time)
        if len(self.bat_events.events) == 0:
            raise Exception("Unable no find batterystats samples. Maybe the profiling session or warm-up time wasn't long "
                            "enough")
        total = 0
        per_component_consumption = {}
        last_event = self.bat_events.events[c_beg_bef]
        last_time = start_time  # self.bat_events.events[c_beg_bef].time if c_beg_bef >= 0 else start_time
        in_bt2 = list(filter(lambda x: x.time >= start_time and x.time >= end_time, self.bat_events.events))
        if c_beg_bef == c_beg_aft or len(in_bt2) == 1:
            # batevents |--|--|--|
            # start-end             |--|
            # or in btween two samples
            delta_time = abs(end_time - start_time)
            total, per_component_consumption = self.calculate_glob_and_component_consumption(last_event,per_component_consumption, delta_time, total)
            return total, per_component_consumption
        #
        for i, x in enumerate(self.bat_events.events[c_beg_aft:]):
            if x.time > end_time:
                #delta_time = end_time - last_time
                break
            delta_time = abs(x.time - last_time)

            total, per_component_consumption = self.calculate_glob_and_component_consumption(last_event, per_component_consumption, delta_time, total)
            last_event = x
            last_time = x.time

        delta_time = end_time - last_time
        if delta_time < 0.0:
            log(time=time.time(), message="Error calculating delta (<0) ", log_sev=LogSeverity.FATAL)
        total, per_component_consumption = self.calculate_glob_and_component_consumption(last_event, per_component_consumption,delta_time, total)
        return total, per_component_consumption

    def calculate_cpu_energy(self, start_time, end_time):
        """calculates cpu energy consumption of device between a timestamp interval
        Args:
            start_time: begin timestamp
            end_time: end timestamp
        Returns:
            total: cpu energy consumption
        """
        if len(self.perf_events.events) == 0:
            raise Exception("Unable no find perfetto samples. Maybe the profiling session or warm-up time wasn't long "
                            "enough")
        c_beg_bef, c_beg_aft = self.perf_events.get_closest_pair(start_time)
        total = 0
        last_event = self.perf_events.events[c_beg_bef]
        last_time = start_time
        tot_time = 0
        in_bt2 = list(filter(lambda x: x.time >= start_time and x.time >= end_time, self.perf_events.events))
        if c_beg_bef == c_beg_aft or len(in_bt2) == 1:
            # perfevent |--|--|--|
            # start-end             |--|
            # or in bt2 2 samples
            delta_time = abs(end_time - start_time)
            l = self.bat_events.get_CPU_samples_in_between(last_time, end_time)
            for sample in l:
                delta, state, voltage = sample[0], sample[1], sample[2]
                cpus_current = last_event.calculate_CPUs_current(state, self.perf_events.power_profile)
                tot_time += delta
                total += (cpus_current) * delta * voltage
            return total

        for i, x in enumerate(self.perf_events.events[c_beg_aft:]):
            if x.time > end_time:
                break
            l = self.bat_events.get_CPU_samples_in_between(last_time, x.time)
            # TODO : test to assert if x.time - last_time  = sum( deltas_of_L )
            for sample in l:
                delta, state, voltage = sample[0], sample[1], sample[2]
                cpus_current = last_event.calculate_CPUs_current(state, self.perf_events.power_profile)
                tot_time += delta
                total += (cpus_current) * delta * voltage
            last_event = x
            last_time = x.time

        # after calcs'''
        # TODO merge with cycle just like with non cpu
        l = self.bat_events.get_CPU_samples_in_between(last_time, end_time)
        for sample in l:
            delta, state, voltage = sample[0], sample[1], sample[2]
            cpus_current = last_event.calculate_CPUs_current(state, self.perf_events.power_profile)
            tot_time += delta
            total += (cpus_current) * delta * voltage
        # TODO just like non cpu
        # print(tot_time)
        return total



    def __extract_power_profile(self, filename):
        """ Extracts power_profile.xml file from the device, by pulling framework-res.apk and using apktool to unzip the apk.
        If the process fails, retrieves DEFAULT_PROFILE filepath
        Args:
            filename: the target name of the file
        Returns:
            filename: the name of the extracted xml file
        """
        # extracting power_profile.xml from device
        res, suc, v = execute_shell_command("adb pull /system/framework/framework-res.apk %s" % self.resources_dir)
        if res == 0:
            cmd = """java -jar {res_dir}/apktool_2.4.0.jar d -s {res_dir}/framework-res.apk -f -o {res_dir}/out_jar_dir/""".format(
                res_dir=self.resources_dir)
            res, suc, v = execute_shell_command(cmd)
            pp_file = self.resources_dir + "/out_jar_dir/res/xml/power_profile.xml"
            if res == 0:
                # cp to profiles, remove out_jar_dir and framework-res.apk
                res, _, _ = execute_shell_command(
                    "cp {extracted_file} \"{res_dir}/profiles/{new_file}\" ; rm -rf {res_dir}/out_jar_dir {res_dir}/framework-res.apk".format(
                        extracted_file=pp_file, new_file=filename, res_dir=self.resources_dir))
                if res == 0:
                    return filename

        return DEFAULT_PROFILE

    def infer_power_profile(self):
        """picks the most appropriate power profile file. power profile files present in self.resources_dir contains a
        device model id in the filename, which is determinated by ro.product.model property. if there is an adequate
        file locally, it retrieves such filename. Otherwise, it extracts the profile from the device
        using __extractPowerProfile.

        Returns:
            filename: the name of the  xml file.
        """
        res, device_model, _ = execute_shell_command("adb shell getprop ro.product.model")
        if res == 0 and device_model != "":
            model_profile_file = """power_profile_{device_model}.xml""".format(
                device_model=device_model.replace(" ", "").strip().lower())
            matching_profiles = mega_find(self.resources_dir, pattern=model_profile_file, maxdepth=2)
            if len(matching_profiles) > 0:
                return matching_profiles[0]
            else:
                # if power profile not present in profiles directory, extract from device
                power_profile = self.__extract_power_profile(model_profile_file)
                #print(power_profile)
                return power_profile
        else:
            return DEFAULT_PROFILE

    @staticmethod
    def __infer_timezone():
        """ Obtains device timezone. if there is no device connected, returns DEFAULT_TIMEZONE.
        Returns:
            tz(str): device timezone
        """
        res, out, err = execute_shell_command("adb shell date")
        default_tz = DEFAULT_TIMEZONE
        if res == 0 and len(out) > 0:
            default_tz = out.split(" ")[-2]
        log("Using timezone: %s" % default_tz)
        return "WET" if default_tz == "WEST" else default_tz

    def unplug_if_fully_charged(self):
        """ virtually unplugs device charger, by calling dumpsys battery unplug."""
        # battery stats file comes empty when battery level == 100
        # using adb to trick device to think it is not charging th battery
        res, o, e = execute_shell_command("adb shell dumpsys battery | grep level | grep 100")
        has_full_charge = res == 0 and "100" in o
        if has_full_charge:
            # mock unplug
            res, o, e = execute_shell_command("adb shell dumpsys battery unplug")
            if res == 0:
                self.unplugged = True
                log("virtually unplugging battery charger while running (battery == 100)", LogSeverity.WARNING)

    def plug_back(self):
        """plugs back the device"""
        res, o, e = execute_shell_command("adb shell dumpsys battery reset")
        self.unplugged = False

    def gen_final_report(self, start_time=None, end_time=None):
        begin = self.perf_events.events[0].time if start_time is None else start_time
        end = self.perf_events.events[-1].time if end_time is None else end_time
        total, per_c, timeline = self.get_consumption_in_between(begin, end)
        res = {
            'total_energy:': total,
            'elapsed_time': end-begin,
            'per_component_consumption': per_c,
            'stats': timeline,
            'method_invocations': 0,
            'diff_methods': 0
        }
        return {'global': res}

    def save_final_report(self, run_id=None, output_filepath=None):
        if output_filepath is None:
            output_filepath = "manafa_resume_%s.json" % (run_id if run_id is not None else 0)
        with open(output_filepath, 'w') as j:
            json.dump(self.gen_final_report(), j)
