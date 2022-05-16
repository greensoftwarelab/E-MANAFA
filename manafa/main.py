import shutil
import sys, os, time, json
import argparse
from manafa.utils.Utils import execute_shell_command, mega_find, get_resources_dir, is_float
from manafa.emanafa import EManafa
from manafa.hunter_emanafa import HunterEManafa
from manafa.utils.Logger import log, LogSeverity

MANAFA_RESOURCES_DIR = get_resources_dir()
MAX_SIZE = sys.maxsize
TO_INSTRUMENT_FILE = os.path.join(MANAFA_RESOURCES_DIR, 'to_instrument_file.txt')
NOT_INSTRUMENT_FILE = os.path.join(MANAFA_RESOURCES_DIR, 'not_instrument_file.txt')
MANAFA_INSPECTOR_URL = "https://greensoftwarelab.github.io/manafa-inspector/"


def has_connected_devices():
    """checks if there are devices connected via adb"""
    res, o, e = execute_shell_command("adb devices -l | grep -v attached")
    return res == 0 and len(o) > 2


def create_manafa(args):
    if args.hunter or args.hunterfile is not None:
        return HunterEManafa(power_profile=args.profile, timezone=args.timezone, resources_dir=MANAFA_RESOURCES_DIR,
            instrument_file=TO_INSTRUMENT_FILE,
            not_instrument_file=NOT_INSTRUMENT_FILE)
    else:
        return EManafa(power_profile=args.profile, timezone=args.timezone, resources_dir=MANAFA_RESOURCES_DIR)


def parse_results(args, manafa):
    if args.directory:
        bstats_files = mega_find(args.directory, pattern="bstats-*", maxdepth=2, type_file='f')
        for b_file in bstats_files:
            b_file_id = os.path.basename(b_file).split("-")[1] #if len(os.path.basename(b_file).split("-")) >
            matching_pft_files = [ x for x in  mega_find(args.directory, pattern="trace-*" ) if b_file_id in x ]
            if len(matching_pft_files) == 0:
                print(" unmatched batstats file")
                continue
            matching_ht_files = [x for x in mega_find(args.directory, pattern="hunter-*") if b_file_id in x]
            if len(matching_ht_files) > 0:
                _, fc = manafa.parse_results(bts_file=b_file, pf_file=matching_pft_files[0], htr_file=matching_ht_files[0])
                shutil.copyfile(fc, os.path.basename(fc))
            else:
                manafa.parse_results(b_file, matching_pft_files[0])
            begin = manafa.perf_events.events[0].time  # first sample from perfetto
            #end = manafa.perf_events.events[-1].time  # last sample from perfetto
            #total, per_c, timeline = manafa.get_consumption_in_between(begin, end)
            #print_profiled_stats(end - begin, total, per_c, timeline)
            out_file = manafa.save_final_report(begin, output_filepath=args.output_file)
            log(f"Output file: {out_file}. You can inspect it with E-MANAFA Inspector in {MANAFA_INSPECTOR_URL}",
                log_sev=LogSeverity.SUCCESS)
            manafa.clean()
    elif args.hunterfile:
        manafa.parse_results(args.batstatsfile, args.perfettofile, args.hunterfile)
        manafa.calculate_function_consumption()
    else:
        manafa.parse_results(args.batstatsfile, args.perfettofile)


def print_profiled_stats(el_time, total_consumption, per_comp_consumption, event_timeline):
    print("--------------------------------------")
    print(f"Total energy consumed: {total_consumption} Joules")
    print(f"Elapsed time: {el_time} secs")
    print("--------------------------------------")
    print("Per-component consumption")
    print(json.dumps(per_comp_consumption, indent=1))
    #print("--------------------------------------")
    #print(json.dumps(event_timeline, indent=1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ht", "--hunter", help="parse hunter logs", action='store_true', default=True)
    parser.add_argument("-p", "--profile", help="power profile file", default=None, type=str)
    parser.add_argument("-t", "--timezone", help="device timezone", default=None, type=str)
    parser.add_argument("-pft", "--perfettofile", help="perfetto file", default=None, type=str)
    parser.add_argument("-bts", "--batstatsfile", help="batterystats file", default=None, type=str)
    parser.add_argument("-htf", "--hunterfile", help="hunter file", default=None, type=str)
    parser.add_argument("-d", "--directory", help="results file directory", default=None, type=str)
    parser.add_argument("-o", "--output_file", help="output file", default=None, type=str)
    parser.add_argument("-s", "--time_in_secs", help="time to profile", default=10, type=int)
    args = parser.parse_args()
    has_device_conn = has_connected_devices()
    invalid_file_args = (args.perfettofile is None or args.batstatsfile is None) and args.directory is None
    if not has_device_conn and invalid_file_args:
        log("Fatal error. No connected devices or result files submitted for analysis", LogSeverity.FATAL)
        exit(-1)
    manafa = create_manafa(args)
    if has_device_conn and invalid_file_args:
        log(f"No perfetto and batstats files as input. profiling for ~{args.time_in_secs} seconds", LogSeverity.WARNING)
        manafa.init()
        manafa.start()
        log("profiling...")
        time.sleep(args.time_in_secs)  # do work
        log("stopping profiler...")
        manafa.stop()
        begin = manafa.perf_events.events[0].time  # first sample from perfetto
        end = manafa.perf_events.events[-1].time  # last sample from perfetto
        total, per_c, timeline = manafa.get_consumption_in_between(begin, end)
        print_profiled_stats(end-begin, total, per_c, timeline)
        out_file = manafa.save_final_report(begin, output_filepath=args.output_file)
        log(f"Output file: {out_file}. You can inspect it with E-MANAFA Inspector in {MANAFA_INSPECTOR_URL}",
            log_sev=LogSeverity.SUCCESS)
    else:
        parse_results(args, manafa)


if __name__ == '__main__':
    main()