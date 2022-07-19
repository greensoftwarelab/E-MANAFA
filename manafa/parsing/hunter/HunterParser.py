import sys, os, re


class HunterParser(object):
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

    def parse_file(self, filepath, functions=[], instrument=False):
        """function to parse traces from filepath file.
        Args:
            filepath: logfile with app traces.
            functions: list of function names to filter.
            instrument: optional paramm to enable or disable function filtering.
        """
        with open(filepath, 'r') as filehandle:
            lines = filehandle.read().splitlines()
            self.parse_history(lines, functions, instrument)

    def parse_history_old_format(self, lines_list, functions, instrument=False, start_time=0, end_time=sys.maxsize):
        """function to parse app traces from a list of lines (lines_list).
                Args:
                    lines_list: list of lines from log file.
                    functions: list of function names to filter.
                    instrument: optional paramm to enable or disable function filtering.
                    start_time: lower timestamp bound.
                    end_time: upper timestmp bound.
                """
        for i, line in enumerate(lines_list):
            if ": " in line:
                line = line.split(": ")[-1]
                if ">>" in line:
                    continue
            if re.match(r"^>", line):
                before_components = re.split('^>', line.replace(" ", ""))
                components = re.split('[,=\[\]]', before_components[1])
                function_name = components[0].replace("$", ".")
                add_function = self.verify_function(function_name, functions, instrument)
                begin_time = components[6]
                if add_function and float(begin_time) >= start_time:
                    if function_name not in self.trace:
                        self.trace[function_name] = {}
                        self.trace[function_name][0] = {'begin_time': float(begin_time) * (pow(10, -3))}
                    else:
                        self.trace[function_name][len(self.trace[function_name])] = {
                            'begin_time': float(begin_time) * (pow(10, -3))}
            elif re.match(r"^<", line):
                before_components = re.split('^<', line.replace(" ", ""))
                components = re.split('[,=\[\] ]', before_components[1])
                function_name = components[0].replace("$", ".")
                add_function = self.verify_function(function_name, functions, instrument)
                close_time = float(components[6])
                if close_time > end_time:
                    # remove func
                    print("todo: remove function from obj")
                if add_function:
                    close_time = components[6]
                    self.update_trace_return(function_name, close_time)
            else:
                pass
                # log("invalid line" + line)

    def parse_history(self, lines_list, functions, instrument=False, start_time=0, end_time=sys.maxsize):
        """function to parse app traces from a list of lines (lines_list).
        Args:
            lines_list: list of lines from log file.
            functions: list of function names to filter.
            instrument: optional paramm to enable or disable function filtering.
            start_time: lower timestamp bound.
            end_time: upper timestmp bound.
        """
        for i, line in enumerate(lines_list):
            if ": " in line:
                line = line.split(": ")[-1]
                if ">>" in line:
                    continue
            if re.match(r"^>", line) and line.strip().endswith("]"):
                self.parse_history_old_format(lines_list[:], functions, instrument=instrument, start_time=0, end_time=end_time)
                return
            elif re.match(r"^>", line):
                before_components = re.split('^>', line)
                components = re.split('[,=\[\]]', before_components[1])
                function_name = components[0].replace("$", ".")
                add_function = self.verify_function(function_name, functions, instrument)
                begin_time = components[1]
                if add_function and float(begin_time) >= start_time:
                    if function_name not in self.trace:
                        self.trace[function_name] = {}
                        self.trace[function_name][0] = {'begin_time': float(begin_time) * (pow(10, -3))}
                    else:
                        self.trace[function_name][len(self.trace[function_name])] = {
                            'begin_time': float(begin_time) * (pow(10, -3))}
            elif re.match(r"^<", line):
                before_components = re.split('^<', line)
                components = re.split('[,=\[\] ]', before_components[1])
                function_name = components[0].replace("$", ".")
                add_function = self.verify_function(function_name, functions, instrument)
                close_time = float(components[1])
                if close_time > end_time:
                    #remove func
                    print("todo: remove function from obj")
                if add_function:
                    close_time = components[1]
                    self.update_trace_return(function_name, close_time)
            else:
                pass
                #log("invalid line" + line)

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

    def add_cpu_consumption_to_trace_file(self, filename, functions, instrument=False):
        new_filename = filename.replace(os.path.basename(filename), os.path.basename(filename).replace("hunter-", "truncated_hunter-"))
        if new_filename == filename:
            new_filename = new_filename +".withcpu"
        with open(filename, 'r+') as fr, open(new_filename, 'w') as fw:
            for line in fr:
                #print(line)
                checked = False
                function_name = None
                function_begin = ">"
                if re.match(r"^>", line):
                    before_components = re.split('^>', line)
                    components = re.split('[,=\[\] ]', before_components[1])
                    function_name = components[0].replace("$", ".")
                elif re.match(r"^<", line):
                    before_components = re.split('^<', line)
                    components = re.split('[,=\[\] ]', before_components[1])
                    function_name = components[0].replace("$", ".")
                    checked = True
                    function_begin = "<"
                add_function = self.verify_function(function_name, functions, instrument) if function_name else None
                if add_function:
                    consumption, time = self.return_cpu_consumption_and_time_by_function(function_name, checked)
                    new_line = function_begin + function_name + " [m=example, " + 'cpu = ' + str(
                        consumption) + ', t = ' + str(time) + ']\n'
                    fw.write(new_line)

        #execute_shell_command("rm %s" % filename)
        return new_filename

    def return_cpu_consumption_and_time_by_function(self, function_name, checked):
        """returns energy consumed and elapsed time of function with function_name-
        Args:
            function_name: name of the function.
            checked: if the start and end time of the function was determined.

        Returns:
            cpu_consumption:
            da_time:
        """
        consumption = 0.0
        cpu_consumption = 0.0
        da_time = 0.0
        for i, times in enumerate(self.trace[function_name]):
            results = self.trace[function_name][i]
            if not results['checked']:
                if checked:
                    consumption = results['consumption']
                    per_component_consumption = results['per_component_consumption']
                    cpu_consumption = per_component_consumption['cpu']

                    da_time = results['end_time'] if 'end_time' in results else self.end_time
                    self.__update_checked(function_name, i)
                    return cpu_consumption, da_time
                da_time = results['begin_time']
                return cpu_consumption, da_time
        return cpu_consumption, da_time

    def __update_checked(self, function_name, position):
        """returns energy consumed and elapsed time of function with function_name-
           Args:
               function_name(str): name of the function.
               position(int): function index (i.e. number of calls so far).
           """
        self.trace[function_name][position].update(
            {
                'checked': True
            }
        )

    def update_trace_return(self, function_name, end_time):
        """updates function return time.
        Args:
            function_name: name of the function.
            end_time: function end time.
        """
        i = len(self.trace[function_name]) - 1 if function_name in self.trace else -1
        while i >= 0:
            times = self.trace[function_name][i]
            if 'end_time' not in times:
                end = float(end_time) * (pow(10, -3))
                times.update({'end_time': end})
                if end > self.end_time:
                    self.end_time = end
                times['elapsed_time'] = times['end_time'] - times['begin_time']
                break
            i -= 1

    # Verify if it is to add the function to hunter_trace or get consumption
    @staticmethod
    def verify_function(function_name, functions, add_function=False):
        if len(functions) == 0:
            return True
        res = not add_function
        for function in functions:
            if function in function_name:
                res = not res
                break
        return res
