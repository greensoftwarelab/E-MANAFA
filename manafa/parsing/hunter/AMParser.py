import sys

from manafa.utils.Logger import log


class AMParser(object):
    """Class that parses traces in log files generated by a custom hunter plugin.

    This class parses method traces contained in log files generated by a custom hunter plugin.

    Attributes:
        trace (dict): method traces.
        boot_time (float): timestamp of the device's last boot.
        end_time (float): timestamp of the last trace.
    """
    def __init__(self, boot_time=0):
        self.trace = {}
        self.boot_time = boot_time
        self.end_time = boot_time

    def parse_file(self, filepath):
        """function to parse traces from filepath file.
        Args:
            filepath: logfile with app traces.
        """
        if filepath is None:
            return
        with open(filepath, 'r') as filehandle:
            lines = filehandle.read().splitlines()
            self.parse_history(lines[1:])


    def parse_history(self, lines_list, start_time=0, end_time=sys.maxsize, col_sep=','):
        """function to parse app traces from a list of lines (lines_list).
        Args:
            lines_list: list of lines from log file.
            start_time: lower timestamp bound.
            end_time: upper timestamp bound.
            col_sep: column separator used in the log file.
        """
        end_time = float(end_time) if end_time != sys.maxsize else float((lines_list[-1].split(',')[1]) if len(lines_list) > 0 else sys.maxsize)
        for i, line in enumerate(lines_list):
            #print(line)
            if len(line) < 3:
                continue
            line = line.strip()
            method_def, begin_time, duration, depth = line.split(col_sep)
            begin_time = self.boot_time + (float(begin_time) * pow(10, -9))  # convert from nanoseconds to seconds
            method_name = method_def.split(' ')[0].replace("\"", '').replace("$", ".").replace(":", "")
            method_hash = str(hash(method_def.split(':')[1] if len(method_def.split(' ')) > 1 else ''))
            function_id = f"{method_name}_{method_hash}"
            duration_secs = float(duration) * pow(10, -9)  # convert from nanoseconds to seconds
            if float(begin_time) >= start_time:
                time_obj = {
                    'begin_time': begin_time,
                    'end_time': begin_time + (duration_secs if duration_secs > 0 else end_time - begin_time),
                    'depth': int(depth),
                    'method_def': method_def,
                }
                if method_name not in self.trace:
                    self.trace[function_id] = {}
                    self.trace[function_id][0] = time_obj
                else:
                    self.trace[function_id][len(self.trace[function_id])] = time_obj
            else:
                #pass
                log("invalid line" + line)

    def add_consumption(self, function_name, position, consumption, per_component_consumption, metrics):
        """updates consumption stats when a line referring a function is parsed.
        Args:
            function_name: name of the function to update.
            position: index in stats. equivalent to number of function calls so far.
            consumption: consumption value.
            per_component_consumption: consumption per component.
            metrics: batterystats during function execution.
        """
        self.trace[function_name][position].update(
            {
                'checked': False,
                'consumption': consumption,
                'per_component_consumption': per_component_consumption,
                'metrics': metrics
            }
        )

    def return_cpu_consumption_and_time_by_function(self, function_name, checked):
        """returns energy consumed and elapsed time of function with function_name-
        Args:
            function_name: name of the function.
            checked: if the start and end time of the function was determined.

        Returns:
            cpu_consumption:
            da_time:
        """
        cpu_consumption = 0.0
        da_time = 0.0
        if not function_name in self.trace:
            return 0, 0
        for i, times in enumerate(self.trace[function_name]):
            results = self.trace[function_name][i]
            if not results['checked']:
                if checked:
                    per_component_consumption = results['per_component_consumption']
                    cpu_consumption = per_component_consumption['cpu']
                    da_time = results['end_time'] if 'end_time' in results else self.end_time
                    self.trace[function_name][i].update( { 'checked': True})
                    return cpu_consumption, da_time
                da_time = results['begin_time']
                return cpu_consumption, da_time
        return cpu_consumption, da_time