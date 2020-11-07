
from os import sys,path
import re,json
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from dateUtils  import convertBatStatTimeToTimeStamp

default_json_path="src/batteryStats/BatteryStatus.json"

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


class BatteryEvent(object):
	"""docstring for BatteryEvent"""
	def __init__(self,time=0.0,val={}):
		self.time=time
		self.updates = val 

	def __str__(self):
		return "time:%f vals =  %s " % (self.time, str(self.updates))

	def __repr__(self):
		return str(self)

	def merge_events(self,event1):
		for ev in event1.updates.keys():
			if ev.startswith("-"):
				self.updates.pop("+"+ev.replace("-","",1), None)
			else:
				self.updates[ev]=event1.updates[ev]

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
		self.runningStuff={}


class BatteryStats(object):
	"""docstring for BatteryStats"""
	def __init__(self,def_file=default_json_path):
		self.events = []
		self.definitions = self.loadDefinitionFile(def_file)
		#self.pidstats= []

	def loadDefinitionFile(self,def_file):
		with open(def_file,"r") as dff:
			return json.load(dff)


	def getDefinitionVal(self,key,val=""):
		if re.sub(r"\+|\-", "", key) in self.definitions["monoval"]:
			return 0 if "-" in key else 1
		elif re.sub(r"\+|\-", "", key) in self.definitions["trival"]:
			return key
		elif re.sub(r"\+|\-", "", key) in self.definitions["numerical"]:
			return val
		elif re.sub(r"\+|\-", "", key) in self.definitions["nominal"]:
			return self.definitions["nominal"][str(key)][val]
		return None

	def isTrival(self,key):
		return re.sub(r"\+|\-", "", key) in self.definitions["trival"]

	def parseStates(self,states):
		accum=False
		accumulator = ""
		latest_state=None
		events={}
		for state in states.split(" "):
			if accum:
				accumulator+=state
				if state.count('\"')%2 != 0:
					#print("acumulou")
					accum = not accum
					accumulator = ""
					#print(accumulator)
				continue		
			if "=" in state:	
				if state.count('\"')%2 != 0:
					accum = True
					accumulator+=state
					continue
				else:
						#print(state)
					key = state.split("=")[0]
					val = state.split("=")[1]
					state = self.getDefinitionVal(key,val)
					if self.isTrival(key):
						print("TODO: split in trival")
						print("%s - %s -%s" %(key,val.split(":")[0],val.split(":")[1]))
						#return key,val.split(":")[0],val.split(":")[1]
						events[key]= {"val": val.split(":")[0] , "val2": val.split(":")[1]}
					else:
						print("%s - %s" %(key,state))
						events[key]=state
			else:
				#print(state)
				st = self.getDefinitionVal(state)
				print("%s - %s" %(state,st))
				
				#print("val "+str(self.getDefinitionVal(state)))
				events[re.sub(r"\+|\-","", state)]=st
		return events
	def parseHistory(self,lines_list):
		for i, line in enumerate(lines_list):
			if re.match(r"^Per-PID Stats", line)or len(line)==0:
				return
			else:
				#self.parseState(lines_list[i:])
				x = re.match(r"^\s*([^\s]+) (\(\d+\)) (\d+) (.*)$", line)
				if x:
					print(x.groups())
					#print("time:" +x.groups()[0])
					time = convertBatStatTimeToTimeStamp(x.groups()[0])
					
					events = self.parseStates(x.groups()[3])
					b = BatteryEvent(time, events )
					self.addUpdate(b)
		

	def addUpdate(self, bat_event):
		if len(self.events)==0:
			self.events.append(bat_event)
		else:	
			last_added = self.events[-1]
			if last_added.time == bat_event.time:
				self.events[-1] = BatteryEvent( last_added.time ,merge_two_dicts(self.events[-1].updates, bat_event.updates))
	
			else:
				print("todo calculate power of last event")
				new_b= BatteryEvent( bat_event.time ,merge_two_dicts(self.events[-1].updates, bat_event.updates))
				self.events.append(new_b)
				print(self.events)
				print("\nuiui\n")

	def parseFile(self,filename):
		print("parsing")
		with open(filename, 'r') as filehandle:
			lines=filehandle.read().splitlines()
		for i, line in enumerate(lines):
			#print(line)
			if re.match(r"^Battery History",line):
				self.parseHistory(lines[i:])
			if re.match(r"^Per-PID Stats:",line):
				print("olha o pid stats")
				return
			else:
				return


if __name__ == '__main__':
	if len(sys.argv)>1:
		x = BatteryStats()
		x.parseFile(sys.argv[1])