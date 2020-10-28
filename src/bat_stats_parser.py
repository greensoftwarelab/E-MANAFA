
import os, sys,re



class State(object):
	"""docstring for State"""
	def __init__(self):	
		super(State, self).__init__()
		self.time=0
		self.oldState = 0
		self.oldState2 = 0
		self.oldLevel = -1
		self.oldStatus = -1
		self.oldHealth = -1
		self.oldPlug = -1
		self.oldTemp = -1
		self.oldVolt = -1
		self.oldChargeMAh = -1
		self.oldModemRailChargeMah = -1
		self.oldWifiRailChargeMah = -1
		self.wakelockTag = None
		self.wakeReasonTag = None
		self.eventCode = None
		self.eventTag = None
		

#The data unit is a number taken from the following list:
# 1: Number of objects
# 2: Number of bytes
# 3: Number of milliseconds
# 4: Number of allocations
# 5: Id
# 6: Percent
# s: Number of seconds (monotonic time)

class BatteryStats(object):
	"""docstring for BatteryStats"""
	def __init__(self):
		self.events = []
		self.pidstats= []

		

class BatteryEvent(object):
	"""docstring for BatteryEvent"""
	def __init__(self):
		super(BatteryEvent, self).__init__()
		self.type="Unknown"
		self.start_time=0
		self.pid=0
		self.desc="Unknown"

		

class BatteryInfo(object):
	"""docstring for BatteryInfo"""
	def __init__(self):
		super(BatteryInfo, self).__init__()
		self.reset_time=0
		self.initial_state={}
		self.events=[]
		

def parseInitialState(lines_list):
	for i, line in enumerate(lines_list):
		if not re.match(r"^(\s)*0", line):
			return
		print(line)


def parseHistory(lines_list):
	bt=BatteryInfo()
	for i, line in enumerate(lines_list):
		if re.match(r"^Per-PID Stats", line)or len(line)==0:
			return
		if re.match(r"^(\s)*0", line):
			parseInitialState(lines_list[i:])
			

def parseFile(filename):
	with open(filename, 'r') as filehandle:
		lines=filehandle.read().splitlines()
	for i, line in enumerate(lines):
		#print(line)
		if re.match(r"^Battery History",line):
			print("ui" + str(i))
			parseHistory(lines[i:])
		if re.match(r"^Per-PID Stats:",line):
			print("olha o pid stats")





if __name__ == '__main__':
	if len(sys.argv)>1:
		parseFile(sys.argv[1])