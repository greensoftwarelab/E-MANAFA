
import os, sys,re


#The data unit is a number taken from the following list:
# 1: Number of objects
# 2: Number of bytes
# 3: Number of milliseconds
# 4: Number of allocations
# 5: Id
# 6: Percent
# s: Number of seconds (monotonic time)

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
		



def parseHistory(lines_list=[]):
	bt=BatteryInfo()
	for line in lines_list[1:]:
		if re.match(r'^[ \t]+0 ', line):
			print(line + " matcha")
			

def parseFile(filename):
	with open(filename, 'r') as filehandle:
		lines=filehandle.read().splitlines()
	parseHistory(lines)



if __name__ == '__main__':
	if len(sys.argv)>1:
		parseFile(sys.argv[1])