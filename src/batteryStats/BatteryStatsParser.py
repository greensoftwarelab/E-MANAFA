
from os import sys,path
import re,json
#sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from PowerProfile import PowerProfile
from dateUtils  import convertBatStatTimeToTimeStamp
import copy
default_json_path="src/batteryStats/BatteryStatus.json"


class BatteryEvent(object):
	"""docstring for BatteryEvent"""
	def __init__(self,time=0.0,vals={}):
		self.time=time
		self.updates = {}
		self.concurrentUpdates={} 
		self.concurrentUpdates["tmpwhitelist"]=[]
		self.concurrentUpdates["job"]=[]
		self.concurrentUpdates["sync"]=[]
		self.concurrentUpdates["top"]=[]
		self.concurrentUpdates["longwake"]=[]
		self.concurrentUpdates["fg"]=[]
		self.concurrentUpdates["proc"]=[]
		self.concurrentUpdates["screenwake"]=[]
		self.concurrentUpdates["pkgactive"]=[]
		self.concurrentUpdates["user"]=[]
		self.concurrentUpdates["userfg"]=[]
		self.concurrentUpdates["wake_lock_in"]=[]
		self.concurrentUpdates["alarm"]=[]

	
		self.addEvents(vals)

	def __str__(self):
		return "time:%f vals =  %s , concs= %s  " % (self.time,str(self.updates),str(self.concurrentUpdates))

	def __repr__(self):
		return str(self)

	def isConcurrent(self,state):
		#return re.match(r"(\+|\-)?(tmpwhitelist|job|sync|top|longwake|fg|proc)", state)
		return state in self.concurrentUpdates

	def addEvents(self,event1):
		for ev in event1.keys():
			#print("->"+ev + "--")
			if ev.startswith("-"):
				conc_update_state = ev.replace("-","",1)
				if self.isConcurrent(conc_update_state):		
					#print("vou tirar conc "+ev)
					self.concurrentUpdates[conc_update_state] = [n for n in self.concurrentUpdates[conc_update_state] if (  n["val"] != event1[ev]["val"] and n["val2"] != event1[ev]["val2"] ) ]
				else:
					#print("vou tirar ev "+ev)
					self.updates.pop(conc_update_state,None)
			else:
				ev_def = ev.replace("+","",1)
				if self.isConcurrent(ev_def):
					self.concurrentUpdates[ev_def].append(event1[ev])	
				else:
					self.updates[ev_def]=event1[ev]


class BatteryStats(object):
	"""docstring for BatteryStats"""
	def __init__(self,def_file=default_json_path):
		self.events = []
		self.definitions = self.loadDefinitionFile(def_file)
		self.powerProfile = None

	def loadPowerProfile(self, xml_profile ):
		self.powerProfile = PowerProfile(xml_profile)

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

		for state in re.sub(r"^ ","",states).split(" "):
			#print("->" +state)
			if accum:
				accumulator+=state
				if state.count('\"')%2 != 0:
					accum = not accum
					accumulator = ""
				continue		
			if "=" in state:	
				if state.count('\"')%2 != 0:
					accum = True
					accumulator+=state
					continue
				else:
					key = state.split("=")[0]
					val = state.split("=")[1]
					state = self.getDefinitionVal(key,val)
					if self.isTrival(key):
						#print("TODO: split in trival")
						#print("%s - %s -%s" %(key,val.split(":")[0],val.split(":")[1]))
						#return key,val.split(":")[0],val.split(":")[1]
						events[key]= {"val": val.split(":")[0] , "val2": val.split(":")[1]}
					else:
						#print("%s = %s" %(key,state))
						events[key]=state
			elif state != "" and state != " ":
				st = self.getDefinitionVal(state)
				#print("%s - %s" %(state,st))
				#print("val "+str(self.getDefinitionVal(state)))
				events[state]=st
			
		return events
	
	def parseHistory(self,lines_list):
		for i, line in enumerate(lines_list):
			if re.match(r"^Per-PID Stats", line)or len(line)==0:
				return
			elif re.match(r"^\s*([^\s]+) (\(\d+\)) (\d+)(.*)?$", line):
				x = re.match(r"^\s*([^\s]+) (\(\d+\)) (\d+)(.*)?$", line)
				#print(x.groups())
				#print("time:" +x.groups()[0])
				time = convertBatStatTimeToTimeStamp(x.groups()[0])
				events = self.parseStates(x.groups()[3])
				
				self.addUpdate(time, events)
			else:
				# TODO Handle DcpuStats and DpstStats
				print("linha invalida" + line)

	def addUpdate(self, time,bat_events):
		if len(self.events)==0:
			self.events.append( BatteryEvent( time,bat_events ))
		else:	
			last_added = self.events[-1]
			if last_added.time == time:
				self.events[-1].addEvents(bat_events)
				
			else:
				# todo try to replace with shallow copy
				bt = copy.deepcopy(self.events[-1])
				bt.time = time
				bt.addEvents(bat_events)
				self.estimatePowerConsumption(bt)
				self.events.append(bt)


	def estimatePowerConsumption(self,bt_event):
		print("----------")
		power = 0.0
		for p,v in self.powerProfile.components.items():
			st = self.determinateComponentCurrent(bt_event,p,v)
			print(st)
			#print(str(p in self.updates)+ " + " +str(p) )	
		return power


	def determinateComponentCurrent(self,bt_event,comp_name, possible_states):
		current = 0.0
		if comp_name == "screen" and "screen" in bt_event.updates:
				on_current = possible_states["on"]
				brightness_level = bt_event.updates["brightness"]
				relative_full_current = ( brightness_level * possible_states["full"] / ( len( self.definitions["nominal"]["brightness"] ) -1) ) 
				current+= on_current + relative_full_current 

		elif comp_name == "ambient" and "screen_doze" in bt_event.updates:
				# power profile might have a defined value for ambient/doze screen consumpri
				doze_current = possible_states["on"]
				current+=doze_current

		return current

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
		#pp = "samples/profiles/power_profile.xml"
		pp = "samples/profiles/power_profile_pixel3a_grapheneos.xml"
		x.loadPowerProfile(pp)
		x.parseFile(sys.argv[1])
		

