import bisect


import re
from enum import Enum
import xml.etree.ElementTree as ET
from manafa.parsing.powerProfile.PowerProfile import PowerProfile
from manafa.utils.Logger import log
from manafa.utils.Utils import execute_shell_command

x="""import time
import subprocess
def executeShCommand(command):

    pipes = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    std_out, std_err = pipes.communicate()
    output = std_out.decode("utf-8").lower()
    if pipes.returncode != 0:
        err_msg = "%s. Code: %s" % (std_err.decode('utf-8').strip(), pipes.returncode)
        print("error executing command %s" % command)
        print(err_msg)
        return -1    
    elif len(std_err)==0:
        return output


def epochToDate(ts):
	return time.ctime(ts)
###"""

def interpolate(x1: float, x2: float, y1: float, y2: float, x: float):
	"""Performs linear interpolation for x between (x1,y1) and (x2,y2) """
	return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)  if (x2-x1)>0 else y1
	#print(val)
	#print("---")
	#return val


class CPU_STATE(Enum):
	SUSPEND = "suspend"
	IDLE = "idle"
	AWAKE = "awake"
	ACTIVE = "active"


class PerfettoCPUEvent(object):
	"""Stores information regarding each cpu frequency in a given time.

	A perfetto  cpufreq event information, corresponding to a line in an results output file in systrace format.
	Attributes:
		time: event_time.
		vals: frequency for each cpu of device.
	"""
	def __init__(self, time=0.0, values=[]):
		self.time=time
		self.vals=[]
		for x in values:
			self.vals.append(x)

	def __str__(self):
		return "time: %f vals =  %s , " % (self.time, str(self.vals))

	def __repr__(self):
		return str(self)

	def init_all(self, default_len=8, val=0):
		"""inits values for each cpu.
		Args:
			default_len: number of cores.
			val: default value.
		"""
		for x in range(0, default_len):
			if len(self.vals) > x:
				self.vals[x] = val
			else:
				self.vals.append(val)

	def update(self, cpu_id,cpu_freq):
		"""update/insert cpufreq val for each cpu id"""
		if len(self.vals)> cpu_id:
			self.vals[cpu_id]=cpu_freq
		else:
			for x in range(len(self.vals)-1, cpu_id):
				self.vals.append(cpu_freq)


	def calculate_CPUs_current(self, state, profile):
		"""given a power profile and a cpu state, returns the instantaneous current being consumed by all cpu cores in that state.
			Args:
				state: cpu state in CPU_STATE values
				profile: power profile class
		"""
		total = 0
		if state not in ["idle", "suspend"]:
			for core_id, freq in enumerate(self.vals):
				bf, aft = profile.get_CPU_core_speed_pair(core_id, freq)
				lin_inter_val = interpolate(bf[0], aft[0], bf[1], aft[1], freq)
				total += lin_inter_val
			total = total / len(self.vals)
		else:
			total = profile.get_CPU_state_current(state)
		return total / 1000


class PerfettoCPUfreqParser(object):
	"""Parses cpu frequency updates from a log file obtained with perfetto.
	Attributes:
		power_profile: current device power profile.
		start_time: lower timestamp bound to consider.
		timezone: device timezone.
	"""
	def __init__(self, power_profile=None, start_time=0.0, timezone="EST"):
		self.events = []
		self.start_time = start_time
		self.power_profile = self.load_power_profile(power_profile) if power_profile is not None else {}

	def get_device_current_frequency_vals(self):
		cpu_vals = execute_shell_command("adb shell cat '/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq' ")[1]
		return cpu_vals.splitlines()

	def start(self):
		start_time = execute_shell_command("adb shell date +%s")[1].strip()
		pce = PerfettoCPUEvent(int(start_time))
		for i, cpu_f in enumerate(self.get_device_current_frequency_vals()):
			pce.update(i, int(cpu_f))
		self.events.append(pce)

	@staticmethod
	def load_power_profile(xml_profile):
		"""Loads power profile from xml_profile filepath.
		Returns:
			object: power profile file. 
		"""
		return PowerProfile(xml_profile)

	def parse_file(self, filename):
		"""parses filename.
		Args:
			filename: path of log file resultant of a profiling session with perfetto.
		"""
		with open(filename, 'r') as filehandle:
			lines = filehandle.read().splitlines()
			self.parse_history(lines)

	def parse_history(self, lines):
		"""parses event from lines.
		Args:
			lines: list of lines from file.
		"""
		for line in lines:
			if line.startswith("#"):
				continue
			z = re.match(r"^\s*([^\s]+)\-(\d+)\s*\(\s*(\d+|\-+)\) \[(\d+)\] (\d+|\.+) ([0-9]*\.[0-9]+|[0-9]+)\: (.*)?$",line)
			if z is not None:
				time = float(z.groups()[5])
				time += self.start_time
				ev_pair = self.parse_event(z.groups()[6])
				if ev_pair is not None:
					cpu_id = ev_pair[0]
					cpu_freq = ev_pair[1]
					self.add_event(time, cpu_id, cpu_freq)
			else:
				raise Exception("Error parsing file")

	def add_event(self, time: float, cpu_id: int, cpu_freq: int):
		"""add or update cpu freq event based on values passed as argument.
		Args:
			time: timestamp of event.
			cpu_id: id of cpu.
			cpu_freq: frequency value.
		"""
		if len(self.events) == 0:
			z = PerfettoCPUEvent(time)
			z.init_all(default_len=8, val=cpu_freq)
			self.events.append(z)
		else:
			last = self.events[-1]
			z = PerfettoCPUEvent(time, last.vals)
			z.update(cpu_id, cpu_freq)
			self.events.append(z)

	def parse_event(self, ev_str):
		""" parse frequency and cpu id from string.
		Args:
			ev_str: string expecting to have the patttern.
		Returns:
			cpu_id(int): id of the cpu.
			cpu_freq(int): frequency value.
		"""
		mat = re.match(r'cpu_frequency: state=(\d+) cpu_id=(\d+)', ev_str)
		if mat:
			cpu_id = int(mat.groups()[1])
			cpu_freq = int(mat.groups()[0])
			return cpu_id, cpu_freq
		return None

	def get_closest_pair(self, time):
		"""return the closest indexes of samples to time.
		Args:
			time: reference time.
		Returns:
			lasti(int): before index.
			i(int): after index.
		"""
		times = self.event_times()
		i = bisect.bisect_right(times, time)  # first event after time
		if i == len(times):
			return max(i - 1, 0), max(i - 1, 0)
		return max(i - 1, 0), i

	def event_times(self):
		"""sorted event timestamps, cached until the event list changes (for bisect lookups)."""
		key = (id(self.events), len(self.events))
		if getattr(self, '_times_key', None) != key:
			self._times = [x.time for x in self.events]
			self._times_key = key
		return self._times


def parse_dumpsys_output(dumpsys_text: str) -> dict:
	"""
    Parses the plain text output from the dumpsys command into a dictionary.

    Args:
        dumpsys_text: The multi-line string output from the adb command.

    Returns:
        A dictionary where keys are the power profile items (e.g., 'cpu.active')
        and values are either floats or lists of floats.
    """
	parsed_data = {}
	lines = dumpsys_text.strip().split('\n')

	for line in lines:
		line = line.strip()

		# Stop at special sections that don't follow the key=value format
		if line.lower().startswith('modem values'):
			break

		# Skip lines that are not key-value pairs
		if '=' not in line:
			continue

		key, value_str = line.split('=', 1)
		key = key.strip()
		value_str = value_str.strip()

		# Check if the value is a list (array)
		if value_str.startswith('[') and value_str.endswith(']'):
			# It's a list. Parse its contents.
			list_content = value_str[1:-1]
			if list_content:
				# Split by comma and convert each element to float
				parsed_value = [float(item.strip()) for item in list_content.split(',')]
			else:
				parsed_value = []
		else:
			# It's a single item. Convert to float.
			try:
				parsed_value = float(value_str)
			except ValueError:
				# Skip if the value is not a valid float
				continue

		parsed_data[key] = parsed_value

	return parsed_data


def generate_power_profile_xml(data: dict, output_filename: str):
	"""
    Generates a power_profile.xml file from a parsed data dictionary.

    Args:
        data: The dictionary generated by parse_dumpsys_output.
        output_filename: The name of the file to save (e.g., 'power_profile.xml').
    """
	# Create the root element <device name="Android">
	root = ET.Element("device", name="Android")

	# Sort keys for a consistent output file
	sorted_keys = sorted(data.keys())

	for key in sorted_keys:
		value = data[key]
		if isinstance(value, list):
			# This is an array
			array_element = ET.SubElement(root, "array", name=key)
			for item in value:
				value_element = ET.SubElement(array_element, "value")
				value_element.text = str(item)
		else:
			# This is a single item
			item_element = ET.SubElement(root, "item", name=key)
			item_element.text = str(value)

	# Create an ElementTree object and write it to a file
	tree = ET.ElementTree(root)

	# Use ET.indent for pretty-printing the XML (available in Python 3.9+)
	# This makes the output human-readable.
	ET.indent(tree, space="\t", level=0)

	tree.write(output_filename, encoding="utf-8", xml_declaration=True)
	log(f"Successfully generated '{output_filename}'")


if __name__ == '__main__':
	# --- Paste the output of 'adb shell dumpsys batterystats --power-profile' here ---
	sample_dumpsys_output = """
    Power Profile: 
        ambient.on=32.0 
        wifi.controller.tx=540.0 
        cpu.active=10.62 
        wifi.controller.rx=39.0 
        modem.controller.idle=156.0 
        camera.avg=900.0 
        video=25.0 
        screen.full.display0=470.0 
        camera.flashlight=240.47 
        modem.controller.rx=145.0 
        gps.voltage=3700.0 
        screen.on=98.0 
        modem.controller.sleep=0.0 
        cpu.suspend=9.28 
        audio=75.0 
        wifi.controller.voltage=3850.0 
        modem.controller.voltage=3700.0 
        wifi.controller.idle=31.0 
        screen.on.display0=98.0 
        screen.full=470.0 
        cpu.cluster_power.cluster0=0.0 
        cpu.cluster_power.cluster1=1.12 
        cpu.idle=22.71 
        cpu.cluster_power.cluster2=2.2 
        ambient.on.display0=32.0 
        cpu.core_speeds.cluster2=[700000.0, 1164000.0, 1296000.0, 1557000.0, 1745000.0, 1885000.0, 1999000.0, 2147000.0, 2294000.0, 2363000.0, 2499000.0, 2687000.0, 2802000.0, 2914000.0, 2943000.0, 2970000.0, 3015000.0, 3105000.0] 
        cpu.core_power.cluster0=[1.27, 5.87, 6.5, 7.93, 10.5, 14.06, 16.18, 17.65, 20.92, 24.67, 34.09, 47.41] 
        gps.signalqualitybased=[28.0, 5.0] 
        cpu.core_power.cluster2=[16.91, 29.84, 39.6, 47.85, 58.03, 66.96, 74.66, 87.45, 102.03, 110.83, 130.63, 165.41, 193.74, 229.21, 238.15, 244.34, 251.35, 253.83] 
        modem.controller.tx=[153.0, 212.0, 292.0, 359.0, 471.0] 
        cpu.core_power.cluster1=[5.4, 8.9, 9.9, 12.65, 14.65, 18.15, 22.65, 25.15, 28.65, 33.9, 46.4, 56.9, 71.15, 81.4, 92.9, 102.4, 124.9] 
        cpu.core_speeds.cluster0=[324000.0, 610000.0, 820000.0, 955000.0, 1098000.0, 1197000.0, 1328000.0, 1425000.0, 1548000.0, 1696000.0, 1849000.0, 1950000.0] 
        cpu.core_speeds.cluster1=[357000.0, 578000.0, 648000.0, 787000.0, 910000.0, 1065000.0, 1221000.0, 1328000.0, 1418000.0, 1549000.0, 1795000.0, 1945000.0, 2130000.0, 2245000.0, 2367000.0, 2450000.0, 2600000.0] 
        cpu.clusters.cores=[4.0, 3.0, 1.0] 
        Modem values:
          drain:SLEEP,RAT:DEFAULT=0.0
          drain:IDLE,RAT:DEFAULT=156.0
          drain:RX,RAT:DEFAULT=145.0
          drain:TX,level:0,RAT:DEFAULT=153.0
    """

	# Define the output file name
	output_xml_file = "power_profile.xml"

	# 1. Parse the text output
	parsed_profile_data = parse_dumpsys_output(sample_dumpsys_output)

	# 2. Generate the XML file from the parsed data
	generate_power_profile_xml(parsed_profile_data, output_xml_file)

#bootTime = float ( executeShCommand ("adb shell cat /proc/stat | grep btime | awk '{print $2}'").strip() )
#print(bootTime)
#print(epochToDate(bootTime))
#x = PerfettoCPUfreqParser(bootTime)
#x.parseFile("/Users/ruirua/repos/petra_like/results/perfetto/trace-1605638909.systrace")
#print(x.events)

