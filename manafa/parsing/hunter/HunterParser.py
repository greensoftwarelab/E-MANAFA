import sys, os, re

class HunterParser(object):
    def __init__(self, boot_time=0):
        self.trace = {}
        self.boot_time = boot_time
        self.end_time = boot_time

    def parse_file(self, filename, functions, instrument=False):
        """array functions to decide which methods collect instrumentation data
        variable instrument to decide if array functions is an array of methods
        to collect information or to discard"""
        with open(filename, 'r') as filehandle:
            lines = filehandle.read().splitlines()
            self.parse_history(lines, functions, instrument)

    def parse_history(self, lines_list, functions, instrument=False, start_time=0, end_time=sys.maxsize):
        for i, line in enumerate(lines_list):
            #print(line)
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
                    #remove func
                    print("todo: remove function from obj")
                if add_function:
                    close_time = components[6]
                    self.update_trace_return(function_name, close_time)
            else:
                pass
                #log("invalid line" + line)

    def add_consumption(self, function_name, position, consumption, per_component_consumption, metrics):
        self.trace[function_name][position].update(
            {
                'checked': False,
                'consumption': consumption,
                'per_component_consumption': per_component_consumption,
                'metrics': metrics
            }
        )

    def add_consumption_to_trace_file(self, filename, functions, instrument=False):
        new_filename = filename.replace(os.path.basename(filename), os.path.basename(filename).replace("hunter-", "truncated_hunter-"))
        with open(filename, 'r+') as fr, open(new_filename, 'w') as fw:
            for line in fr:
                #print(line)
                checked = False
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

                add_function = self.verify_function(function_name, functions, instrument)
                if add_function:
                    consumption, time = self.return_consumption_and_time_by_function(function_name, checked)
                    new_line = function_begin + function_name + " [m=example, " + 'cpu = ' + str(
                        consumption) + ', t = ' + str(time) + ']\n'
                    fw.write(new_line)

        #execute_shell_command("rm %s" % filename)
        return new_filename

    '''
        Returns cpu consumption instead total consumption
    '''
    def return_consumption_and_time_by_function(self, function_name, checked):
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
        self.trace[function_name][position].update(
            {
                'checked': True
            }
        )

    def update_trace_return(self, function_name, end_time):
        i = len(self.trace[function_name]) - 1 if function_name in self.trace else -1
        while i >= 0:
            times = self.trace[function_name][i]
            if 'end_time' not in times:
                end = float(end_time) * (pow(10, -3))
                times.update({'end_time': end})
                if end > self.end_time:
                    self.end_time = end
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
