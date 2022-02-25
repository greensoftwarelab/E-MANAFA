

import re
from enum import Enum

from manafa.parsing.powerProfile.PowerProfile import PowerProfile

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
	"""Perform linear interpolation for x between (x1,y1) and (x2,y2) """
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
	"""Stores information regarding each cpu frequency in a given time
		A perfetto  cpufreq event information, corresponding to a line in an results output file in systrace format
		Attributes:
		time: event_time
		vals: frequency for each cpu of device
	"""
	def __init__(self, time=0.0, values=[]):
		self.time=time
		self.vals=[]
		for x in values:
			self.vals.append(x)

	def __str__(self):
		return "time:%f vals =  %s , " % (self.time,str(self.vals))

	def __repr__(self):
		return str(self)

	def initAll(self, default_len=8, val=0):
		"""Inits vals for each cpu"""
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


	def calculateCPUsCurrent(self,state, profile):
		"""given a power profile and a cpu state, returns the instantaneous current being consumed by all cpu cores in that state
			Args:
				state: cpu state in CPU_STATE values
				profile: power profile class
		"""
		total=0
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
	def __init__(self, power_profile=None, start_time=0.0, timezone="EST"):
		self.events = []
		self.start_time = start_time
		self.power_profile = self.load_power_profile(power_profile) if power_profile is not None else {}

	def load_power_profile(self, xml_profile):
		return PowerProfile(xml_profile)

	def parse_file(self, filename):
		with open(filename, 'r') as filehandle:
			lines=filehandle.read().splitlines()
			self.parse_history(lines)

	def parse_history(self, lines):
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

	def add_event(self, time, cpu_id, cpu_freq):
		if len(self.events) == 0:
			z = PerfettoCPUEvent(time)
			z.initAll(default_len=8, val=cpu_freq)
			self.events.append(z)
		else:
			last = self.events[-1]
			z = PerfettoCPUEvent(time, last.vals)
			z.update(cpu_id,cpu_freq)
			self.events.append(z)

	def parse_event(self, ev_str):
		mat = re.match(r'cpu_frequency: state=(\d+) cpu_id=(\d+)', ev_str)
		if mat:
			cpu_id=int(mat.groups()[1])
			cpu_freq=int(mat.groups()[0])
			return cpu_id,cpu_freq

	def get_closest_pair(self, time):
		lasti = 0
		for i, x in enumerate(self.events):
			if x.time > time:
				return lasti, i
			lasti = i
		return lasti, lasti

#bootTime = float ( executeShCommand ("adb shell cat /proc/stat | grep btime | awk '{print $2}'").strip() )
#print(bootTime)
#print(epochToDate(bootTime))
#x = PerfettoCPUfreqParser(bootTime)
#x.parseFile("/Users/ruirua/repos/petra_like/results/perfetto/trace-1605638909.systrace")
#print(x.events)

