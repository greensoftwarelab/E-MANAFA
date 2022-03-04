""" This module contains ENUMs that store state values of batterystats events.

BatteryStatsConstants contains constants associated with batterystats events and respective meaning.
"""

import os
import re, json
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from manafa.parsing.powerProfile.PowerProfile import PowerProfile
from manafa.utils.Utils import get_resources_dir
from manafa.utils.dateUtils import convertBatStatTimeToTimeStamp, batStatResetTimeToTimeStamp
import copy
from manafa.utils.Logger import log, LogSeverity

DEFAULT_JSON_PATH = os.path.join(get_resources_dir(), "batteryStats", "BatteryStatus.json")



def safe_division(a, b):
    """function to safely perform division between numbers to avoid division by 0.
        Args:
            a (float): base.
            a (float): quote.

        Returns:
            int: the result of the division.
        """
    z = 1 if b == 0 else b
    return a / z


class BatteryEvent(object):
    """Class to store information information parsed from the lines of batterystats history events.

    This class stores information of one or more lines (when consecutive lines have the same timestamp)
    of batterystats history events.

    Attributes:
        time (float): Stores timestamp of event (s.ms).
        updates (dict): stores component updates (components referred in power_profile.xml) registered in time timestamp.
        current (dict): stores instant current being consumed by each component.
        concurrentUpdates (dict); stores information regarding other updates that are not directly related to energy
         consumption.

    """

    def __init__(self, time=0.0, vals={}):
        """Init Battery event with parsed information.

        Args:
           time (float): timestamp of event (s.ms).
           vals (dict): events registered in batterystats history line(s).
        """
        self.time = time
        self.updates = {}
        self.currents = {}
        self.concurrentUpdates = {"tmpwhitelist": [], "job": [], "sync": [], "top": [], "longwake": [], "fg": [],
                                  "proc": [], "screenwake": [], "pkgactive": [], "user": [], "userfg": [],
                                  "wake_lock_in": [], "alarm": []}
        self.add_events(vals)

    def __str__(self):
        return "time:%f vals =  %s , concs= %s  " % (self.time, str(self.updates), str(self.concurrentUpdates))

    def __repr__(self):
        return str(self)

    def is_concurrent(self, state):
        """checks if is a concurrent update (aka event not related to hardware/sensor state change).

        Args:
           state (str): timestamp of event (s.ms).

        Returns:
            bool: True if successful, False otherwise.
        """
        # return re.match(r"(\+|\-)?(tmpwhitelist|job|sync|top|longwake|fg|proc)", state)
        return state in self.concurrentUpdates

    def get_current_of_batStatEvent(self):
        """gets total current being consumed by the current state of hardware usage.
        Args:
           state (str): timestamp of event (s.ms).

        Returns:
            float: total current being consumed.
        """
        currs = {}
        total = 0
        for v, x in self.currents.items():
            try:
                z = float(x)
                currs[v] = z / 1000
                total += z
            except ValueError:
                currs[v] = 0
                continue
        return total / 1000, currs

    def get_voltage_value(self):
        """gets current voltage value (last value recorded in history lines).

        Returns:
            float: total current value.
        """
        return float(self.updates["volt"]) / 1000 if "volt" in self.updates else 0

    def add_events(self, new_events):
        """Adds a set of events to the current state.
        Args:
           new_events (dict): set of events.
        """
        for ev in new_events.keys():
            # print("->"+ev + "--")
            if ev.startswith("-"):
                conc_update_state = ev.replace("-", "", 1)
                if self.is_concurrent(conc_update_state):
                    self.concurrentUpdates[conc_update_state] = [n for n in self.concurrentUpdates[conc_update_state] if
                                                                 (n["val"] != new_events[ev]["val"] and n["val2"] !=
                                                                  new_events[ev]["val2"])]
                else:
                    self.updates.pop(conc_update_state, None)
            else:
                ev_def = ev.replace("+", "", 1)
                if self.is_concurrent(ev_def):
                    self.concurrentUpdates[ev_def].append(new_events[ev])
                else:
                    self.updates[ev_def] = new_events[ev]


class BatteryStatsParser(object):
    """Class that handles parsing of batterystats history events

    This class parses and batterystats history events from files parsed using parseFile function. It starts by load
    information contained in the device power profile file and also the current state values known by the profiler,
    stored in definitions attribute.

    Attributes:
        events (:obj:`list` of :obj:`BatteryEvent`): stores BatteryEvents by order of occurence.
        definitions (dict): stores definitions ok known states support by batterystats and manafa.
        powerProfile (:obj:`PowerProfile`): stores information parsed from power profile file.
        android_version (int): Android release version.
        start_time (int): initial timestamp inferred from first line of batstats history.
        timezone (str): current device timezone.
    """
    def __init__(self, powerProfile=None, timezone="EST", def_file=DEFAULT_JSON_PATH, android_version=10):
        self.events = []
        self.definitions = self.load_definition_file(def_file)
        self.powerProfile = PowerProfile(powerProfile) if powerProfile is not None else {}
        self.android_version = android_version
        self.start_time = 0
        self.timezone = timezone  # adb shell  date +"%Z %z"

    @staticmethod
    def load_definition_file(def_file):
        """loads definitions attribute from json file
        Args:
            def_file (str): filepath.
        """
        with open(def_file, "r") as dff:
            return json.load(dff)

    def get_definition_val(self, key, val=""):
        """return value of component from key and opt val.
        Args:
            key(str): key that identifies component.
            val(str): optional sub key.
        Returns:
            int: value.
        """
        res = re.sub(r"\+|\-", "", key)
        if res in self.definitions["monoval"]:
            return 0 if "-" in key else 1
        elif res in self.definitions["trival"]:
            return key
        elif res in self.definitions["numerical"]:
            return val
        elif res in self.definitions["nominal"]:
            return self.definitions["nominal"][str(key)][val]
        return None

    def is_trival(self, key):
        """check if is a component with more than 2 values associated.
        Args:
            key: component key.

        Returns:
            bool: result of check.
        """
        return re.sub(r"\+|\-", "", key) in self.definitions["trival"]

    def parse_states(self, states):
        """Parses states from batstats history line.
        Args:
            states: string containing the state updates.

        Returns:
            dict: parsed events
        """
        accum = False
        accumulator = ""
        latest_state = None
        events = {}
        for state in re.sub(r"^ ", "", states).split(" "):
            # print("->" +state)
            if accum:
                accumulator += state
                if state.count('\"') % 2 != 0:
                    accum = not accum
                    accumulator = ""
                continue
            if "=" in state:
                if state.count('\"') % 2 != 0:
                    accum = True
                    accumulator += state
                    continue
                else:
                    key = state.split("=")[0]
                    val = state.split("=")[1]
                    state = self.get_definition_val(key, val)
                    if self.is_trival(key):
                        # print("%s - %s -%s" %(key,val.split(":")[0],val.split(":")[1]))
                        # return key,val.split(":")[0],val.split(":")[1]
                        events[key] = {"val": val.split(":")[0], "val2": "".join(val.split(":")[1:])}
                    else:
                        # print("%s = %s" %(key,state))
                        events[key] = state
            elif state != "" and state != " ":
                st = self.get_definition_val(state)
                # print("%s - %s" %(state,st))
                # print("val "+str(self.getDefinitionVal(state)))
                events[state] = st
        return events

    def parse_history(self, lines_list):
        """Parse history events from list of lines read from file.

        Parses history events and stores them in  the respective attribute fields.
        Args:
            lines_list(:obj:`list` of :obj:`str`): list of lines.
        """
        for i, line in enumerate(lines_list):
            if re.match(r"^Battery History \([0-9]", line):
                # header, ignore
                continue
            if re.match(r"^Per-PID Stats", line) or len(line) == 0:
                return
            elif re.match(r"^\s*([^\s]+) (\(\d+\)) (\d+)(.*)?$", line):
                x = re.match(r"^\s*([^\s]+) (\(\d+\)) (\d+)(.*)?$", line)
                time = convertBatStatTimeToTimeStamp(x.groups()[0], timezone=self.timezone)
                time += self.start_time
                # print(time)
                events = self.parse_states(x.groups()[3])
                self.add_update(time, events)
            elif re.match(r"^\s*0 (\(\d+\)) (.*)?$", line):
                x = re.match(r"^\s*0 (\(\d+\)) (.*)?$", line)
                if "RESET:TIME" in x.groups()[1]:
                    self.start_time = batStatResetTimeToTimeStamp((x.groups()[1]).replace("RESET:TIME: ", ""),
                                                                  self.timezone)
                # print(epochToDate(self.start_time))
            else:
                # TODO Handle DcpuStats and DpstStats
                # print(line)
                log("Unrecognized patter in line of batstats file", LogSeverity.WARNING)

    def add_update(self, time, bat_events):
        """Adds new event updates to current state.

        Args:
            time(int): timestamp of new events.
            bat_events(:obj:`list` of :obj:`dict`):
        """
        if len(self.events) == 0:
            bt = BatteryEvent(time, bat_events)
            self.estimate_current_consumption(bt)
            self.events.append(bt)
        else:
            last_added = self.events[-1]
            if last_added.time == time:
                self.events[-1].add_events(bat_events)

            else:
                # TODO try to replace with shallow copy
                bt = copy.deepcopy(self.events[-1])
                bt.time = time
                bt.add_events(bat_events)
                self.estimate_current_consumption(bt)
                self.events.append(bt)

    def estimate_current_consumption(self, bt_event):
        """estimates current power being consumed by event.
        Args:
            bt_event(str): key of the event.
        """
        power = {}
        for p, v in self.powerProfile.components.items():
            st = self.determinate_component_current(bt_event, p, v)
            power[p] = st
        # print("%s %s" %(p , str(st)))
        bt_event.currents = power

    def get_closest_pair(self, time):
        """returns closest events of a given timestamp time.
        Args:
            time(float): timestamp.
        Returns:
            int, int: index of the closest events.
        """
        lasti = 0
        for i, x in enumerate(self.events):
            if x.time > time:
                return lasti, i
            lasti = i
        return lasti, lasti

    def get_events_in_between(self, start_time, end_time):
        """get batstat events occured between start_time and end_time.
        Args:
            start_time(int): start timestamp.
            end_time(int): end timestamp.

        Returns:
            dict: events occurred.

        """
        metrics = {}
        if (end_time - start_time) <= 0:
            return metrics
        c_beg_bef, c_beg_aft = self.get_closest_pair(start_time)
        # {'health: [(event_state,start,end, pctage_duration)], ..}
        prev_time = self.events[c_beg_aft].time if len(self.events) > 0 else start_time
        fst_time = prev_time
        for ev in self.events[c_beg_aft:]:
            if ev.time > end_time:
                break
            for kup, upval in ev.updates.items():
                metrics[kup] = [] if kup not in metrics else metrics[kup]
                contains_update_val = metrics[kup][-1][0] == upval if len(
                    metrics[kup]) > 0 else None  # next(filter(lambda x: x[0] == upval, metrics[kup]), None)
                if not contains_update_val:
                    if len(metrics[kup]) > 0:
                        # update previous state
                        duration_pctage = 100 * ((ev.time - metrics[kup][-1][1]) / (end_time - start_time))
                        metrics[kup][-1] = (
                            metrics[kup][-1][0], metrics[kup][-1][1], ev.time, duration_pctage)  # last_time?
                    init_time = start_time if fst_time == ev.time else ev.time
                    duration_pctage = 100 * ((end_time - init_time) / (end_time - start_time))
                    metrics[kup].append((upval, init_time, end_time, duration_pctage))
            # concs
            for cup, cupval in ev.concurrentUpdates.items():
                metrics[cup] = [] if cup not in metrics else metrics[cup]
                # detect pushes
                for c_i, cval in enumerate(cupval):
                    # is_in_metrics = metrics[cup][-1][0]['val'] == cval['val'] and metrics[cup][-1][0]['val2'] == cval['val2']  if len(metrics[cup]) > 0 else False
                    is_in_metrics = next(filter(
                        lambda x: x[0]['val'] == cval['val'] and x[0]['val2'] == cval['val2'] and x[2] == end_time,
                        metrics[cup]), None)
                    if not is_in_metrics:
                        # new state, add
                        init_time = start_time if prev_time == ev.time else ev.time
                        duration_pctage = 100 * ((end_time - init_time) / (end_time - start_time))
                        metrics[cup].append((cval, init_time, end_time, duration_pctage))
                # detect pops
                for i, val_of_metrics in enumerate(metrics[cup]):
                    this_ev_contains_val = next(filter(
                        lambda t: t['val'] == val_of_metrics[0]['val'] and t['val2'] == val_of_metrics[0]['val2'],
                        cupval), None)
                    if not this_ev_contains_val:
                        # was popped, update
                        already_popped = val_of_metrics[2] != end_time
                        if not already_popped:
                            prev_start_time = val_of_metrics[1]
                            duration_pctage = 100 * ((ev.time - prev_start_time) / (end_time - start_time))
                            metrics[cup][i] = (val_of_metrics[0], prev_start_time, ev.time, duration_pctage)
            prev_time = ev.time
        return metrics

    def get_CPU_samples_in_between(self, start_time, end_time):
        """returns cpu states recorded between start and end time.
        Args:
            start_time(int): start timestamp.
            end_time(int): end timestamp.

        Returns:
            dict: states occurred.

        """
        l = []
        last_ev = self.events[0] if len(self.events) > 0 else None
        last_time = start_time
        for x in self.events:
            if x.time > start_time and x.time < end_time:
                delta = x.time - last_time
                state = last_ev.currents["cpu"]
                voltage = last_ev.get_voltage_value()  # float(last_ev.updates["volt"])
                pair = (delta, state, voltage)
                l.append(pair)
                last_time = x.time
            last_ev = x
        last_delta = end_time - last_time
        last_state = last_ev.currents["cpu"]
        last_voltage = last_ev.get_voltage_value()  # float(last_ev.updates["volt"])
        last_pair = (last_delta, last_state, last_voltage)
        l.append(last_pair)
        return l

    def determinate_component_current(self, bt_event, comp_name, possible_states):
        """calculates current being consumed during bt_event by component identified by comp_name.

        Args:
            bt_event: event.
            comp_name: component name.
            possible_states: possible states of the component.

        Returns:
            float: current being consumed.

        """
        current = 0.0
        curravg = 0
        avg_ct = 0
        # screen
        if comp_name == "screen" and "screen" in bt_event.updates:
            on_current = possible_states["on"]
            brightness_level = bt_event.updates["brightness"] if "brightness" in bt_event.updates else 1
            relative_full_current = (brightness_level * possible_states["full"] / (
                        len(self.definitions["nominal"]["brightness"]) - 1))
            current += on_current + relative_full_current

        elif comp_name == "ambient" and "screen_doze" in bt_event.updates:
            # power profile might have a defined value for ambient/doze screen consumpri
            doze_current = possible_states["on"]
            current += doze_current

        # camera/flashlight
        elif comp_name == "camera":
            if "camera" in bt_event.updates:
                # usually available as avg consumption (Intended as a rough estimate for an application running a preview and capturing approximately 10 full-resolution pictures per minute.)
                cam_current = possible_states["avg"]
                current += cam_current

            if "flashlight" in bt_event.updates:
                flash_curr = possible_states["flashlight"]
                current += flash_curr
        # dsp
        elif comp_name == "dsp":
            if "video" in bt_event.updates:
                video_curr = possible_states["video"] if comp_name == "dsp" else possible_states
                current += video_curr

            if "audio" in bt_event.updates:
                audio_curr = possible_states["audio"] if comp_name == "dsp" else possible_states
                current += audio_curr

        # audio
        elif comp_name == "video" and "video" in bt_event.updates:
            video_curr = possible_states
            current += video_curr
        # video
        elif comp_name == "audio" and "audio" in bt_event.updates:
            audio_curr = possible_states
            current += audio_curr

        # wifi
        elif comp_name == "wifi" and "wifi_running" in bt_event.updates:
            on_current = possible_states["on"] if "on" in possible_states else 0
            on_current += possible_states["controller"]["idle"] if (
                        "controller" in possible_states and "idle" in possible_states["controller"]) else 0
            current += on_current
            if "wifi_scan" in bt_event.updates:
                if "scan" in possible_states:
                    current += possible_states["scan"]
                if "controller" in possible_states:
                    curravg = 0
                    avg_ct = 0
                    if "tx" in possible_states["controller"]:
                        curravg += possible_states["controller"]["tx"]
                        avg_ct += 1
                    if "rx" in possible_states["controller"]:
                        curravg += possible_states["controller"]["rx"]
                        avg_ct += 1
                    current += safe_division(curravg, avg_ct)
            elif "wifi_radio" in bt_event.updates:
                current += possible_states["active"] if "active" in possible_states else 0
                if "controller" in possible_states:
                    curravg = 0
                    avg_ct = 0
                    if "tx" in possible_states["controller"]:
                        curravg += possible_states["controller"]["tx"]
                        avg_ct += 1
                    if "rx" in possible_states["controller"]:
                        curravg += possible_states["controller"]["rx"]
                        avg_ct += 1
                    current += safe_division(curravg, avg_ct)

        # gps
        elif comp_name == "gps":
            if "signalqualitybased" in possible_states:  # and "gps_signal_quality" in bt_event.updates:
                # considerate gps signal quality
                if "gps_signal_quality" in bt_event.updates:
                    val = 1 if bt_event.updates["gps_signal_quality"] == "good" else 0
                    current += possible_states["signalqualitybased"][val]
            if "on" in possible_states and "gps" in bt_event.updates:
                current += possible_states["on"]

        # bluetooth
        elif comp_name == "bluetooth":
            if self.android_version < 7 or "controller" not in possible_states:
                # account blue on and active vals
                if "ble_scan" in bt_event.updates:
                    current += possible_states["active"] if "active" in possible_states else 0
                    current += possible_states["on"] if "on" in possible_states else 0
                elif "bluetooth" in bt_event.updates:
                    current += possible_states["on"] if "on" in possible_states else 0
            elif "controller" in possible_states:
                current += possible_states["controller"]["idle"] if ("idle" in possible_states["controller"]) else 0
                if "ble_scan" in bt_event.updates:
                    if "tx" in possible_states["controller"]:
                        curravg += possible_states["controller"]["tx"]
                        avg_ct += 1
                    if "rx" in possible_states["controller"]:
                        curravg += possible_states["controller"]["rx"]
                        avg_ct += 1
                    current += safe_division(curravg, avg_ct)

        # radio =  modem
        elif comp_name == "radio":
            # radio.on
            if "phone_scanning" in bt_event.updates:
                # radio.scanning
                current += possible_states["scanning"] if "scanning" in possible_states else 0

            elif "mobile_radio" in bt_event.updates:
                on_vals = list(possible_states["on"]) if "on" in possible_states else []
                signal_stren = bt_event.updates[
                    "phone_signal_strength"] if "phone_signal_strength" in bt_event.updates else 0
                if signal_stren >= len(on_vals) and len(on_vals) > 0:
                    current += on_vals[-1]
                elif len(on_vals) > 0:
                    current += on_vals[signal_stren]
            # radio.active == mobile_radio - transmiting

        elif comp_name == "modem":
            # same as radio
            if "phone_scanning" in bt_event.updates:
                curravg = 0
                avg_ct = 0
                if "tx" in possible_states["controller"]:
                    on_vals = possible_states["controller"]["tx"] if "tx" in possible_states["controller"] else []
                    signal_stren = bt_event.updates[
                        "phone_signal_strength"] if "phone_signal_strength" in bt_event.updates else 0
                    if signal_stren > len(on_vals) and len(on_vals) > 0:
                        curravg += on_vals[-1]
                    elif len(on_vals) > 0:
                        curravg += on_vals[signal_stren]
                    avg_ct += 1
                if "rx" in possible_states["controller"]:
                    curravg += possible_states["controller"]["rx"]
                    avg_ct += 1
                current += safe_division(curravg, avg_ct)
            elif "mobile_radio" in bt_event.updates:
                current += possible_states["idle"] if "idle" in possible_states else 0
        # cpu
        elif comp_name == "cpu":
            # retrieve just the component state
            # if phone has multiple cpu_clusters and that info is present in power profile file
            # only for devices with heterogeneous CPU architectures.
            # print(possible_states)
            # has_multiple_cpu_clusters= "clusters" in possible_states and "cores" in possible_states["clusters"] and  len(possible_states["clusters"]["cores"])>1
            # if has_multiple_cpu_clusters:
            # cores_per_cluster = possible_states["clusters"]["cores"]
            # calculate energy per cluster
            # if areInMinCPUFreq(bt_event.updates["cpufreq"] , possible_states):
            # assume is just awake

            #		current += possible_states["awake"]
            #		else:

            # calculate active state
            #			current += 0 # possible_states["awake"] if "awake" in possible_states else 0
            #			print("TODO Calculate power according to freq")

            #	else:
            if "running" in bt_event.updates:
                # is active or just awake
                # if "awake" in possible_states and areInMinCPUFreq(bt_event.updates["cpufreq"] , possible_states):
                # if areInMinCPUFreq(bt_event.updates["cpufreq"] , possible_states):
                # assume is just awake

                #	current += possible_states["awake"]
                # else:
                # calculate active state
                #	current += 0 # possible_states["awake"] if "awake" in possible_states else 0
                #	print("TODO Calculate power according to freq")
                current = "active"
            else:
                # cpu in idle state
                # current+= possible_states["idle"] if "idle" in possible_states else 0
                current = "idle"

        return current

    def parse_file(self, filepath):
        """parses events ands stores event from file with output from dumpsys batterystats command.
        Args:
            filepath: output filepath.
        """
        with open(filepath, 'r') as ff:
            lines = ff.read().splitlines()
            self.parse_history(lines)

# if __name__ == '__main__':
# if len(sys.argv)>1:
# pp = "samples/profiles/power_profile.xml"
# pp = "samples/profiles/power_profile_pixel3a_grapheneos.xml"
# x = BatteryStatsParser(powerProfile=pp,timezone="WET")
# x.parseFile(sys.argv[1])
