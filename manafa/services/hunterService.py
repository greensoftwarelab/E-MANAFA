import time

from textops import cat

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
        self.trace = {}

    def start(self, run_id=None):
        self.clean()

    def stop(self, run_id=None):
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        time.sleep(1)
        filename = self.results_dir + "/hunter-%s-%s.log" % (run_id, str(self.boot_time))
        execute_shell_command("adb logcat -d | grep -io \"[<>].*m=example.*]\" > %s" % filename)
        return filename

    def clean(self):
        execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)
        execute_shell_command("adb logcat -c")  # or   adb logcat -b all -c

    # parses function to other module HunterParser
    def parseFile(self, filename):
        with open(filename, 'r') as filehandle:
            lines = filehandle.read().splitlines()
            self.parseHistory(lines)

    def parseHistory(self, lines_list):
        not_functions = ["<init>", "get", "set", "Util"]
        for i, line in enumerate(lines_list):
            if re.match(r"^>", line):
                before_components = re.split('^>', line.replace(" ",""))
                components = re.split('[,=\[\]]',  before_components[1])
                function_name = components[0].replace("$", "_")
                add_function = True
                for not_function in not_functions:
                    if not_function in function_name:
                        add_function = False
                        break
                if add_function:
                    begin_time = components[6]
                    if function_name not in self.trace:
                        self.trace[function_name] = {}
                        self.trace[function_name][0] = {'begin_time': float(begin_time) * (pow(10, -3))}
                    else:
                        self.trace[function_name][len(self.trace[function_name])] = {
                            'begin_time': float(begin_time) * (pow(10, -3))}
            elif re.match(r"^<", line):
                before_components = re.split('^<', line.replace(" ",""))
                components = re.split('[,=\[\] ]', before_components[1])
                function_name = components[0].replace("$", "_")
                add_function = True
                for not_function in not_functions:
                    if not_function in function_name:
                        add_function = False
                        break
                if add_function:
                    end_time = components[6]
                    self.updateTraceReturn(function_name, end_time)
            else:
                log("invalid line")

    def addConsumption(self, function_name, position, consumption, per_component_consumption, metrics):
        self.trace[function_name][position].update(
            {
                'checked': False,
                'consumption': consumption,
                'per_component_consumption': per_component_consumption,
                'metrics': metrics
            }
        )

    def addConsumptionToTraceFile(self, filename):
        not_functions = ["<init>", "get", "set", "Util"]

        split_filename = re.split("/", filename)

        new_filename = "/".join(split_filename[0: len(split_filename) - 1])
        new_filename += '[edited]' + split_filename[len(split_filename) - 1]

        with open(filename, 'r+') as fr, open(new_filename, 'w') as fw:
            for line in fr:
                checked = False
                function_begin = ">"
                if re.match(r"^>", line):
                    before_components = re.split('^>', line)
                    components = re.split('[,=\[\] ]', before_components[1])
                    function_name = components[0].replace("$", "_")
                elif re.match(r"^<", line):
                    before_components = re.split('^<', line)
                    components = re.split('[,=\[\] ]', before_components[1])
                    function_name = components[0].replace("$", "_")
                    checked = True
                    function_begin = "<"

                add_function = True
                for not_function in not_functions:
                    if not_function in function_name:
                        add_function = False
                        break
                if add_function:
                    consumption, time = self.returnConsumptionAndTimeByFunction(function_name, checked)
                    new_line = function_begin + function_name + " [m=example, " + 'cpu = ' + str(consumption) + ', t = ' + str(time) + ']\n'
                    fw.write(new_line)

        execute_shell_command("rm %s" % filename)
        return new_filename

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

    def updateTraceReturn(self, function_name, end_time):
        i = len(self.trace[function_name]) - 1
        while i >= 0:
            times = self.trace[function_name][i]
            if 'end_time' not in times:
                times.update({'end_time': float(end_time) * (pow(10, -3))})
                break
            i -= 1
