from .service import Service

import re
from ..utils.Utils import execute_shell_command
from manafa.utils.Logger import log


class HunterService(Service):
    def __init__(self, boot_time=0, output_res_folder="hunter"):
        Service.__init__(self, output_res_folder)
        self.trace = {}
        self.boot_time = boot_time

    def config(self, **kwargs):
        pass

    def init(self, boot_time=0, **kwargs):
        self.boot_time = boot_time
        self.clean()

    def start(self, file_id=None):
        if file_id is None:
            file_id = execute_shell_command("date +%s")[1].strip()
        filename = self.results_dir + "/hunter-%s-%s.log" % (file_id, str(self.boot_time))
        log("Hunter file:  %s" % filename)
        execute_shell_command("adb logcat -d | grep -io \"[<>].*m=example.*]\" > %s" % filename)
        return filename

    def stop(self):
        pass

    def clean(self):
        execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)
        execute_shell_command("adb logcat -c")  # or   adb logcat -b all -c

    # parses function to other module HunterParser
    def parseFile(self, filename):
        with open(filename, 'r') as filehandle:
            lines = filehandle.read().splitlines()
            self.parseHistory(lines)

    def parseHistory(self, lines_list):
        not_functions = ["<init>", "get", "set"]

        for i, line in enumerate(lines_list):
            if re.match(r"^>", line):
                before_components = re.split('^>', line)
                components = re.split('[,=\[\] ]', before_components[1])
                function_name = components[0]
                add_function = True
                for not_function in not_functions:
                    if not_function in function_name:
                        add_function = False
                        break
                if add_function:
                    begin_time = components[13]
                    if function_name not in self.trace:
                        self.trace[function_name] = {}
                        self.trace[function_name][0] = {'begin_time': float(begin_time) * (pow(10, -3))}
                    elif len(self.trace[function_name]) not in self.trace[function_name]:
                        self.trace[function_name][len(self.trace[function_name])] = {
                            'begin_time': float(begin_time) * (pow(10, -3))}
            elif re.match(r"^<", line):
                before_components = re.split('^<', line)
                components = re.split('[,=\[\] ]', before_components[1])
                function_name = components[0]
                add_function = True
                for not_function in not_functions:
                    if not_function in function_name:
                        add_function = False
                        break
                if add_function:
                    end_time = components[13]
                    self.trace[function_name][len(self.trace[function_name]) - 1].update(
                        {'end_time': float(end_time) * (pow(10, -3))})
            else:
                print("linha invalida" + line)

    def addConsumption(self, function_name, position, consumption, per_component_consumption):
        self.trace[function_name][position].update(
            {
                'checked': False,
                'consumption': consumption,
                'per_component_consumption': per_component_consumption
            }
        )

    def addConsumptionToTraceFile(self, filename):
        not_functions = ["<init>", "get", "set"]
        with open(filename, 'r+') as fr, open(filename, 'r+') as fw:
            for line in fr:
                checked = False
                if re.match(r"^>", line):
                    before_components = re.split('^>', line)
                    components = re.split('[,=\[\] ]', before_components[1])
                    function_name = components[0]
                elif re.match(r"^<", line):
                    before_components = re.split('^<', line)
                    components = re.split('[,=\[\] ]', before_components[1])
                    function_name = components[0]
                    checked = True
                add_function = True
                for not_function in not_functions:
                    if not_function in function_name:
                        add_function = False
                        break
                if add_function:
                    consumption, time = self.returnConsumptionAndTimeByFunction(function_name, checked)
                    cpu = re.split('cpu = \d+', line)
                    if len(cpu) < 2:
                        fw.write(line)
                    else:
                        fw.write(cpu[0] + 'cpu = ' + str(consumption) + ', t = ' + str(time) + ']\n')
            fw.truncate()

    def returnConsumptionAndTimeByFunction(self, function_name, checked):
        consumption = 0.0
        time = 0.0
        for i, times in enumerate(self.trace[function_name]):
            results = self.trace[function_name][i]
            if not results['checked']:
                if checked:
                    consumption = results['consumption']
                    time = results['end_time']
                    self.updateChecked(function_name, i)
                    return consumption, time
                time = results['begin_time']
                return consumption, time
        return consumption, time

    def updateChecked(self, function_name, position):
        self.trace[function_name][position].update(
            {
                'checked': True
            }
        )
