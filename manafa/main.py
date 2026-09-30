import shutil
import sys, os, time, json
import argparse

from manafa.am_emanafa import AMEManafa
from manafa.services.perfettoService import convert_to_systrace
from manafa.utils.Utils import execute_shell_command, mega_find, get_resources_dir
from manafa.emanafa import EManafa
from manafa.hunter_emanafa import HunterEManafa
from manafa.heap_emanafa import HeapEManafa
from manafa.utils.Logger import log, LogSeverity
from manafa.utils.BatteryDrainCalculator import BatteryDrainCalculator

MANAFA_RESOURCES_DIR = get_resources_dir()
MAX_SIZE = sys.maxsize
MANAFA_INSPECTOR_URL = "https://greensoftwarelab.github.io/manafa-inspector/"


def validate_start():
    res, o, e = execute_shell_command("adb shell getprop ro.build.version.release")
    is_above_android_8 = res == 0 and int(o.split(".")[0]) >= 9
    if not is_above_android_8:
        raise Exception("Unable to run E-Manafa on devices with version < Android 9")


def has_connected_devices():
    """checks if there are devices connected via adb"""
    res, o, e = execute_shell_command("adb devices -l | grep -v attached")
    return res == 0 and len(o) > 2


def export_to_json(data, filepath):
    """Export profiling data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    log(f"Detailed results exported to: {filepath}", log_sev=LogSeverity.INFO)


def export_to_csv(data, filepath):
    """Export profiling data to CSV file."""
    import csv
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)

        if 'energy' in data:
            writer.writerow(['ENERGY PROFILING RESULTS'])
            writer.writerow(['Power Rail', 'Energy (Joules)'])
            writer.writerow(['TOTAL', f"{data['energy']['total']:.2f}"])
            writer.writerow([])
            writer.writerow(['Individual Rails:'])
            for rail, energy in sorted(data['energy']['by_rail'].items(), key=lambda x: x[1], reverse=True):
                writer.writerow([rail, f"{energy:.2f}"])
            writer.writerow([])

        if 'memory' in data:
            writer.writerow(['MEMORY PROFILING RESULTS'])
            writer.writerow(['Counter', 'Min (MB)', 'Avg (MB)', 'Max (MB)', 'Samples'])
            for counter in ['MemTotal', 'MemFree', 'MemAvailable', 'Buffers', 'Cached', 'Active', 'Inactive']:
                if counter in data['memory']:
                    stats = data['memory'][counter]
                    writer.writerow([
                        counter,
                        f"{stats['min_mb']:.2f}",
                        f"{stats['avg_mb']:.2f}",
                        f"{stats['max_mb']:.2f}",
                        stats['samples']
                    ])
            writer.writerow([])

        if 'battery_drain' in data:
            writer.writerow(['BATTERY DRAIN ANALYSIS'])
            drain = data['battery_drain']
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Design Capacity (mAh)', f"{drain['design_capacity_mah']:.2f}"])
            writer.writerow(['Current Voltage (V)', f"{drain['current_voltage_v']:.3f}"])
            if 'temperature_c' in drain:
                writer.writerow(['Temperature (°C)', f"{drain['temperature_c']:.1f}"])
            if 'battery_level_percent' in drain:
                writer.writerow(['Battery Level (%)', drain['battery_level_percent']])
            writer.writerow(['Health Multiplier', f"{drain['health_multiplier']:.2f}"])
            writer.writerow(['Effective Capacity (mAh)', f"{drain['effective_capacity_mah']:.2f}"])
            writer.writerow(['Total Battery Energy (Wh)', f"{drain['total_battery_energy_wh']:.3f}"])
            writer.writerow(['Consumed Energy (J)', f"{drain['consumed_energy_joules']:.2f}"])
            writer.writerow(['Consumed Energy (Wh)', f"{drain['consumed_energy_wh']:.6f}"])
            writer.writerow(['Battery Drain (%)', f"{drain['battery_drain_percentage']:.6f}"])

    log(f"Detailed results exported to: {filepath}", log_sev=LogSeverity.INFO)


def display_new_profiler_results(emanafa, profile_mode, battery_drain_info=None):
    """Display results from new enhanced profiler."""
    print("\n" + "="*70)
    print("PROFILING RESULTS")
    print("="*70)

    total_energy = 0
    if profile_mode in ['energy', 'both']:
        if hasattr(emanafa, 'power_rails_energy') and emanafa.power_rails_energy:
            total_energy = emanafa.power_rails_energy['total']
            print(f"\n ENERGY CONSUMPTION:")
            print(f"  Total: {total_energy:.2f} Joules ({total_energy/3600:.4f} Wh)")

            #show top 5 rails
            rails = emanafa.power_rails_energy.get('by_rail', {})
            if rails:
                sorted_rails = sorted(rails.items(), key=lambda x: x[1], reverse=True)[:5]
                print(f"\n  Top Power Rail Consumers:")
                for rail, energy in sorted_rails:
                    print(f"    {rail}: {energy:.2f} J")
        else:
            print("\n No energy data available")

    if profile_mode in ['memory', 'both']:
        if hasattr(emanafa, 'memory_stats') and emanafa.memory_stats:
            mem = emanafa.memory_stats
            print(f"\nSYSTEM MEMORY STATISTICS:")

            #show Total RAM
            if 'MemTotal' in mem:
                total_ram = mem['MemTotal']['avg_mb']
                print(f"  Total RAM: {total_ram:.2f} MB ({total_ram/1024:.2f} GB)")

            #calculate and show Memory Used (Total - Available)
            if 'MemTotal' in mem and 'MemAvailable' in mem:
                total = mem['MemTotal']['avg_mb']
                avail = mem['MemAvailable']

                used_min = total - avail['max_mb']  #when available is max, used is min
                used_avg = total - avail['avg_mb']
                used_max = total - avail['min_mb']  #when available is min, used is max

                print(f"\n  Memory Used:")
                print(f"    Min: {used_min:.2f} MB  |  Avg: {used_avg:.2f} MB  |  Max: {used_max:.2f} MB")

            print(f"\n  (Detailed breakdown of all counters saved to JSON file)")
        else:
            print("\n  No memory data available")

    print("="*70)

    #print battery drain information if available and we have energy data
    if battery_drain_info and total_energy > 0:
        calculator = BatteryDrainCalculator()
        print(calculator.format_battery_drain_report(battery_drain_info))


def create_manafa(args):
    #check if we should use EManafa instead of AMEManafa
    #use EManafa when: force_legacy is set, OR using new profiling modes (energy/memory/both)
    should_use_emanafa = (
        getattr(args, 'force_legacy', False) or
        (hasattr(args, 'profile_mode') and args.profile_mode and args.profile_mode != 'legacy')
    )

    if args.heap:
        return HeapEManafa(app_package_name=args.app_package)

    #hunter mode takes priority
    if args.hunter or args.hunterfile is not None:
        return HunterEManafa(power_profile=args.profile, timezone=args.timezone, resources_dir=MANAFA_RESOURCES_DIR)

    #if app package is specified
    elif args.app_package is not None:
        if should_use_emanafa:
            #use EManafa for legacy mode or new energy/memory modes
            if getattr(args, 'force_legacy', False):
                log("Using EManafa with legacy profiler (app package specified)", log_sev=LogSeverity.INFO)
            else:
                log("Using EManafa with app package (AM profiling disabled for new energy/memory modes)", log_sev=LogSeverity.INFO)

            manafa = EManafa(power_profile=args.profile, timezone=args.timezone, resources_dir=MANAFA_RESOURCES_DIR)
            manafa.app = args.app_package

            #set profiler mode
            if getattr(args, 'force_legacy', False):
                manafa.profiler_mode = 'legacy'
            elif hasattr(args, 'profile_mode') and args.profile_mode:
                manafa.profiler_mode = args.profile_mode

            return manafa
        else:
            #use AMEManafa for app-specific profiling (default behavior)
            manafa = AMEManafa(app_package_name=args.app_package, power_profile=args.profile, timezone=args.timezone,
                               resources_dir=MANAFA_RESOURCES_DIR)
            if hasattr(args, 'profile_mode') and args.profile_mode:
                manafa.profiler_mode = args.profile_mode
            return manafa

    #system-wide profiling (no app package)
    else:
        manafa = EManafa(power_profile=args.profile, timezone=args.timezone, resources_dir=MANAFA_RESOURCES_DIR)
        #set profiler mode
        if getattr(args, 'force_legacy', False):
            manafa.profiler_mode = 'legacy'
        elif hasattr(args, 'profile_mode') and args.profile_mode:
            manafa.profiler_mode = args.profile_mode
        return manafa


def parse_results(args, manafa):
    if args.directory:
        bstats_files = mega_find(args.directory, pattern="bstats-*", maxdepth=2, type_file='f')
        for b_file in bstats_files:
            b_file_id = os.path.basename(b_file).split("-")[1]
            matching_pft_files = [x for x in mega_find(args.directory, pattern="trace-*") if b_file_id in x]
            if len(matching_pft_files) == 0:
                print(" unmatched batstats file")
                continue

            is_converted = matching_pft_files[0].endswith('.systrace')
            if not is_converted:
                matching_pft_files[0] = convert_to_systrace(matching_pft_files[0])
            matching_ht_files = [x for x in mega_find(args.directory, pattern="hunter-*") if b_file_id in x]
            if len(matching_ht_files) > 0:
                _, fc = manafa.parse_results(bts_file=b_file, pf_file=matching_pft_files[0], htr_file=matching_ht_files[0])
                if fc is not None:
                    shutil.copyfile(fc, os.path.basename(fc))
            else:
                manafa.parse_results(b_file, matching_pft_files[0])
            begin = manafa.perf_events.events[0].time if len(manafa.perf_events.events) > 1 else manafa.bat_events.events[0].time
            out_file = manafa.save_final_report(begin, output_filepath=args.output_file)
            log(f"Output file: {out_file}. You can inspect it with E-MANAFA Inspector in {MANAFA_INSPECTOR_URL}",
                log_sev=LogSeverity.SUCCESS)

    elif args.hunterfile:
        manafa.parse_results(args.batstatsfile, args.perfettofile, args.hunterfile)
        manafa.calculate_function_consumption()
    else:
        manafa.parse_results(args.batstatsfile, args.perfettofile)
    manafa.clean()


def print_heap_stats(heap_stats, top=10):
    """prints the classes retaining the most memory in the last heap dump."""
    classes = heap_stats['classes']
    print("--------------------------------------")
    print(f"Heap dumps: {len(heap_stats['dump_timestamps'])}, classes: {len(classes)}")
    print(f"Top {top} classes by retained bytes (last dump; per-dump series in the output file):")
    ranked = sorted(classes.items(), key=lambda kv: kv[1]['retained_bytes'][-1], reverse=True)[:top]
    for name, c in ranked:
        print(f"  {name}: retained={c['retained_bytes'][-1]} B, instances={c['instance_count'][-1]}")
    print("--------------------------------------")


def print_profiled_stats(el_time, total_consumption, per_comp_consumption, event_timeline, battery_drain_info=None):
    print("--------------------------------------")
    print(f"Total energy consumed: {total_consumption} Joules")
    print(f"Elapsed time: {el_time} secs")
    print("--------------------------------------")
    print("Per-component consumption")
    print(json.dumps(per_comp_consumption, indent=1))

    #print battery drain information if available
    if battery_drain_info:
        calculator = BatteryDrainCalculator()
        print(calculator.format_battery_drain_report(battery_drain_info))


def main():
    parser = argparse.ArgumentParser(
        description='E-MANAFA: Energy and Memory profiler for Android applications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Legacy profiler (old method)
  python3 manafa/main.py -a com.android.chrome -s 30 --force-legacy
  
  # New energy profiling (default with power rails)
  python3 manafa/main.py -a com.android.chrome -s 30 -pm energy
  
  # Memory profiling only
  python3 manafa/main.py -a com.android.chrome -s 30 -pm memory

  # Per-class Java heap profiling (debuggable/profileable app, Android 11+)
  python3 manafa/main.py -a com.android.chrome -s 30 -pm memory --heap
  
  # Export detailed results
  python3 manafa/main.py -a com.android.chrome -s 30 -pm energy -of json -o results.json
        """
    )
    
    # Existing arguments
    parser.add_argument("-ht", "--hunter", help="parse hunter logs", action='store_true', default=False)
    parser.add_argument("-p", "--profile", help="power profile file", default=None, type=str)
    parser.add_argument("-t", "--timezone", help="device timezone", default=None, type=str)
    parser.add_argument("-pft", "--perfettofile", help="perfetto file", default=None, type=str)
    parser.add_argument("-bts", "--batstatsfile", help="batterystats file", default=None, type=str)
    parser.add_argument("-htf", "--hunterfile", help="hunter file", default=None, type=str)
    parser.add_argument("-d", "--directory", help="results file directory", default=None, type=str)
    parser.add_argument("-o", "--output_file", help="output file", default=None, type=str)
    parser.add_argument("-s", "--time_in_secs", help="time to profile", default=0, type=int)
    parser.add_argument("-a", "--app_package", help="package of app to profile", default=None, type=str)
    parser.add_argument("-cmd", "--command", help="command to profile", default=None, type=str)

    #new enhanced profiling arguments
    parser.add_argument("-pm", "--profile-mode",
                       choices=['legacy', 'energy', 'memory', 'both'],
                       default='energy',
                       help='Profiling mode: legacy (old profiler), energy (power rails), memory (system memory), or both (default: energy)')

    parser.add_argument("-of", "--output-format",
                       choices=['json', 'csv'],
                       default='json',
                       help='Output format for detailed results (default: json)')

    parser.add_argument("--force-legacy", action='store_true',
                       help='Force use of legacy profiler even if device supports new features')
    parser.add_argument("--heap", action='store_true',
                       help='With -pm memory: per-class Java heap profiling (java_hprof heap dumps) '
                            'instead of system memory counters. Requires -a')
    args = parser.parse_args()
    if args.heap and (args.profile_mode != 'memory' or args.app_package is None):
        parser.error("--heap requires -pm memory and -a <package>")
    
    #warnings for new modes
    if args.profile_mode == 'both' and not args.force_legacy:
        log("WARNING: Profiling both energy and memory simultaneously may introduce overhead.", 
            log_sev=LogSeverity.WARNING)
        log("Consider running separate sessions for most accurate results.", log_sev=LogSeverity.WARNING)
    
    if args.force_legacy:
        args.profile_mode = 'legacy'
        log("Using legacy profiler", log_sev=LogSeverity.INFO)
    
    has_device_conn = has_connected_devices()
    invalid_file_args = (args.perfettofile is None or args.batstatsfile is None) and args.directory is None
    
    if not has_device_conn and invalid_file_args:
        log("Fatal error. No connected devices or result files submitted for analysis", LogSeverity.FATAL)
        exit(-1)
    
    if args.heap and not (has_device_conn and invalid_file_args):
        log("Fatal error. --heap supports live profiling only (connected device, no result files)", LogSeverity.FATAL)
        exit(-1)

    validate_start()
    manafa = create_manafa(args)
    
    if has_device_conn and invalid_file_args:
        #live profiling mode
        print(f"\n{'='*70}")
        print(f"E-MANAFA Profiling")
        print(f"{'='*70}")
        print(f"Mode: {args.profile_mode.upper()}{' (heap)' if args.heap else ''}")
        if args.app_package:
            print(f"App: {args.app_package}")
        print(f"Duration: {args.time_in_secs} seconds" if args.time_in_secs > 0 else "Duration: Manual stop")
        print(f"{'='*70}\n")
        
        manafa.init(clean=True)
        manafa.start()
        log("profiling...")

        if args.command is not None:
            log("executing command to profile: %s" % args.command)
            os.system(args.command)
            log("executed command")
        elif args.time_in_secs == 0:
            input("press any key to stop monitoring")
        else:
            log(f"Profiling for ~{args.time_in_secs} seconds", LogSeverity.INFO)
            time.sleep(args.time_in_secs)
            log("stopping profiler...")
        
        manafa.stop()

        #create battery drain calculator
        battery_calculator = BatteryDrainCalculator()

        #display results based on profiler type
        if args.heap:
            out_file = manafa.save_final_report(output_filepath=args.output_file)
            print_heap_stats(manafa.heap_stats)
            log(f"Output file: {out_file}", log_sev=LogSeverity.SUCCESS)
        elif args.profile_mode == 'legacy' or args.force_legacy:
            #legacy output
            if len(manafa.perf_events.events) > 1 or len(manafa.bat_events.events) > 0:
                begin = manafa.perf_events.events[0].time if len(manafa.perf_events.events) > 1 else manafa.bat_events.events[0].time
                end = manafa.perf_events.events[-1].time if len(manafa.perf_events.events) > 1 else manafa.bat_events.events[-1].time
                try:
                    total, per_c, timeline = manafa.get_consumption_in_between(begin, end)

                    # Calculate battery drain
                    battery_drain_info = battery_calculator.calculate_battery_drain(total)

                    print_profiled_stats(end-begin, total, per_c, timeline, battery_drain_info)
                    out_file = manafa.save_final_report(begin, output_filepath=args.output_file)
                    log(f"Output file: {out_file}. You can inspect it with E-MANAFA Inspector in {MANAFA_INSPECTOR_URL}",
                        log_sev=LogSeverity.SUCCESS)
                except Exception as e:
                    log(f"Unable to compute legacy stats: {e}", log_sev=LogSeverity.WARNING)
                    log("Tip: increase profiling time (e.g., -s 60) or allow a short warm-up before stopping.", log_sev=LogSeverity.INFO)
            else:
                log("No profiling events captured. Legacy profiler requires perfetto events.", log_sev=LogSeverity.WARNING)
                log("The trace files were saved but could not be parsed.", log_sev=LogSeverity.INFO)
        else:
            #new enhanced profiler output
            #calculate battery drain if we have energy data
            battery_drain_info = None
            if args.profile_mode in ['energy', 'both'] and hasattr(manafa, 'power_rails_energy') and manafa.power_rails_energy:
                total_energy = manafa.power_rails_energy.get('total', 0)
                if total_energy > 0:
                    battery_drain_info = battery_calculator.calculate_battery_drain(total_energy)

            display_new_profiler_results(manafa, args.profile_mode, battery_drain_info)

            #export detailed results
            results = {
                'mode': args.profile_mode,
                'app': args.app_package,
                'duration_seconds': args.time_in_secs,
                'timestamp': time.time()
            }

            if args.profile_mode in ['energy', 'both'] and hasattr(manafa, 'power_rails_energy'):
                results['energy'] = manafa.power_rails_energy

            if args.profile_mode in ['memory', 'both'] and hasattr(manafa, 'memory_stats'):
                results['memory'] = manafa.memory_stats

            #add battery drain info to results
            if battery_drain_info:
                results['battery_drain'] = battery_drain_info

            #auto-generate filename if not specified
            if not args.output_file and ('energy' in results or 'memory' in results):
                timestamp = int(time.time())
                args.output_file = f"emanafa_{args.profile_mode}_{timestamp}.{args.output_format}"

            #export
            if args.output_file and ('energy' in results or 'memory' in results):
                if args.output_format == 'json':
                    export_to_json(results, args.output_file)
                else:
                    export_to_csv(results, args.output_file)

                print(f"\nDetailed results saved to: {args.output_file}\n")
    else:
        #file parsing mode (existing functionality)
        parse_results(args, manafa)


if __name__ == '__main__':
    main()