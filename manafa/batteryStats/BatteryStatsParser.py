import re,json
#sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from collections import Iterable

from manafa.powerProfile.PowerProfile import PowerProfile
from manafa.utils.Utils import get_pack_dir
from manafa.utils.dateUtils import convertBatStatTimeToTimeStamp,batStatResetTimeToTimeStamp
import copy

DEFAULT_JSON_PATH = get_pack_dir() +"/batteryStats/BatteryStatus.json"


KNOWN_VALUES=set(
	"screen.on"
	#TODO put here all values in https://source.android.com/devices/tech/power/values
)


def areInMinCPUFreq( cpu_freq , possible_cpu_states  ):
	possible_freqs = possible_cpu_states["speeds"] if "speeds" in possible_cpu_states else []
	if len(possible_freqs)==0:
		possible_freqs = possible_cpu_states["core_speeds"] if "core_speeds" in possible_cpu_states else []
		if len(possible_freqs)>0:
			possible_freqs = sum(possible_freqs.values(),[]) 

	#tem que ser os 2 tempos absolutos
	#print(possible_freqs)
	return False

def safe_division(a,b):
	z = 1 if b==0 else b
	return a / z

class BatteryEvent(object):
	"""docstring for BatteryEvent"""
	def __init__(self,time=0.0,vals={}):
		self.time=time
		self.updates = {}
		self.currents = {}
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

	def getCurrentOfBatStatEvent(self):
		currs = {}
		total = 0
		for v, x in self.currents.items():
			try:
				z = float(x)
				currs[v] = z / 1000
				total += z
			except ValueError:
				currs[v]=0
				continue		
		return total/1000, currs

	def getVoltageValue(self):
		return float(self.updates["volt"]) / 1000 if "volt" in self.updates else 0

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


class BatteryStatsParser(object):
	"""docstring for BatteryStatsParser"""
	def __init__(self, powerProfile=None , timezone="EST", def_file=DEFAULT_JSON_PATH, android_version=10):
		self.events = []
		self.definitions = self.loadDefinitionFile(def_file)
		self.powerProfile = self.loadPowerProfile(powerProfile) if powerProfile is not None else {}
		self.android_version = android_version
		self.start_time = 0
		self.timezone = timezone # adb shell  date +"%Z %z"

	def loadPowerProfile(self, xml_profile ):
		return PowerProfile(xml_profile)

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
			if re.match(r"^Battery History \([0-9]", line):
				#header, ignore
				continue
			if re.match(r"^Per-PID Stats", line)or len(line)==0:
				return
			elif re.match(r"^\s*([^\s]+) (\(\d+\)) (\d+)(.*)?$", line):
				x = re.match(r"^\s*([^\s]+) (\(\d+\)) (\d+)(.*)?$", line)
				time   = convertBatStatTimeToTimeStamp(x.groups()[0], timezone=self.timezone)
				time  += self.start_time
				#print(time)
				events = self.parseStates(x.groups()[3])
				self.addUpdate(time, events)
			elif re.match(r"^\s*0 (\(\d+\)) (.*)?$", line):
				x = re.match(r"^\s*0 (\(\d+\)) (.*)?$", line)
				if "RESET:TIME" in x.groups()[1]:
					self.start_time= batStatResetTimeToTimeStamp((x.groups()[1]).replace("RESET:TIME: ",""), self.timezone )		
					#print(epochToDate(self.start_time))
			else:
				# TODO Handle DcpuStats and DpstStats
				print("linha invalida" + line)

	def addUpdate(self, time,bat_events):
		if len(self.events)==0:
			bt = BatteryEvent( time,bat_events )
			self.estimateCurrentConsumption(bt)
			self.events.append(bt )
		else:	
			last_added = self.events[-1]
			if last_added.time == time:
				self.events[-1].addEvents(bat_events)
				
			else:
				# todo try to replace with shallow copy
				bt = copy.deepcopy(self.events[-1])
				bt.time = time
				bt.addEvents(bat_events)
				self.estimateCurrentConsumption(bt)
				self.events.append(bt)


	def estimateCurrentConsumption(self,bt_event):
		power={}
		for p,v in self.powerProfile.components.items():
			st = self.determinateComponentCurrent(bt_event,p,v)
			power[p]=st
			#print("%s %s" %(p , str(st)))
		bt_event.currents=power
		

	def getCPUSamplesInBetween(self,start_time, end_time ):
		l =[]
		last_ev = self.events[0] if len(self.events)>0 else None
		last_time = start_time
		for x in self.events:
			if x.time > start_time and x.time < end_time:
				delta = x.time - last_time
				state = last_ev.currents["cpu"]
				voltage = last_ev.getVoltageValue() #float(last_ev.updates["volt"])
				pair = (delta, state,voltage)
				l.append(pair)
				last_time= x.time
			last_ev = x
		# 
		last_delta = end_time - last_time
		last_state = last_ev.currents["cpu"]
		last_voltage = last_ev.getVoltageValue() #float(last_ev.updates["volt"])
		last_pair = ( last_delta, last_state,last_voltage)
		l.append(last_pair)
		return l

	def determinateComponentCurrent(self,bt_event,comp_name, possible_states):
		current = 0.0
		curravg=0
		avg_ct=0
		# screen
		if comp_name == "screen" and "screen" in bt_event.updates:
				on_current = possible_states["on"]
				brightness_level = bt_event.updates["brightness"] if "brightness" in bt_event.updates else 1
				relative_full_current = ( brightness_level * possible_states["full"] / ( len( self.definitions["nominal"]["brightness"] ) -1) ) 
				current+= on_current + relative_full_current 

		elif comp_name == "ambient" and "screen_doze" in bt_event.updates:
				# power profile might have a defined value for ambient/doze screen consumpri
				doze_current = possible_states["on"]
				current+=doze_current

		# camera/flashlight 
		elif comp_name == "camera":
			if "camera" in bt_event.updates:
				#usually available as avg consumption (Intended as a rough estimate for an application running a preview and capturing approximately 10 full-resolution pictures per minute.)
				cam_current = possible_states["avg"]
				current+=cam_current
		
			if "flashlight" in bt_event.updates:
				flash_curr = possible_states["flashlight"]
				current+=flash_curr
		# dsp
		elif comp_name == "dsp":
			if "video" in bt_event.updates:
				video_curr = possible_states["video"] if comp_name == "dsp" else possible_states
				current+=video_curr

			if "audio" in bt_event.updates:
				
				audio_curr = possible_states["audio"] if comp_name == "dsp" else possible_states
				current+=audio_curr
		
		# audio
		elif comp_name == "video" and "video" in bt_event.updates:
			video_curr = possible_states
			current += video_curr
		# video
		elif comp_name == "audio" and "audio" in bt_event.updates:
			audio_curr = possible_states
			current += audio_curr

		# wifi 
		elif comp_name == "wifi" and "wifi_running" in bt_event.updates:
			on_current = possible_states["on"] if "on" in possible_states else 0
			on_current += possible_states["controller"]["idle"] if ( "controller" in possible_states and "idle" in possible_states["controller"] ) else 0
			current+= on_current
			if "wifi_scan" in bt_event.updates:
				if "scan" in possible_states:
					current+= possible_states["scan"]
				if "controller" in possible_states:
					curravg=0
					avg_ct =0
					if "tx" in possible_states["controller"]:
						curravg+=possible_states["controller"]["tx"]
						avg_ct+=1
					if "rx" in possible_states["controller"]:
						curravg+=possible_states["controller"]["rx"]
						avg_ct+=1
					current += safe_division(curravg, avg_ct)
			elif "wifi_radio" in bt_event.updates:
				current+= possible_states["active"] if "active" in possible_states else 0
				if "controller" in possible_states:
					curravg=0
					avg_ct =0
					if "tx" in possible_states["controller"]:
						curravg+=possible_states["controller"]["tx"]
						avg_ct+=1
					if "rx" in possible_states["controller"]:
						curravg+=possible_states["controller"]["rx"]
						avg_ct+=1
					current += safe_division(curravg, avg_ct)

		# gps 
		elif comp_name == "gps":
			if "signalqualitybased" in possible_states: # and "gps_signal_quality" in bt_event.updates:
				# considerate gps signal quality
				if "gps_signal_quality" in bt_event.updates:
					val = 1 if bt_event.updates["gps_signal_quality"] == "good" else 0
					current+= possible_states["signalqualitybased"][val]
			if "on" in 	possible_states and "gps" in bt_event.updates:
				current+= possible_states["on"]
		
		#bluetooth
		elif comp_name == "bluetooth":
			if self.android_version<7 or "controller" not in possible_states:
				#account blue on and active vals
				if "ble_scan" in  bt_event.updates:
					current+=  possible_states["active"] if "active" in possible_states else 0
					current+=  possible_states["on"] if "on" in possible_states else 0
				elif "bluetooth" in  bt_event.updates:
					current+=  possible_states["on"] if "on" in possible_states else 0
			elif "controller" in possible_states:
				current += possible_states["controller"]["idle"] if ( "idle" in possible_states["controller"] ) else 0
				if "ble_scan" in  bt_event.updates:
					if "tx" in possible_states["controller"]:
						curravg+=possible_states["controller"]["tx"]
						avg_ct+=1
					if "rx" in possible_states["controller"]:
						curravg+=possible_states["controller"]["rx"]
						avg_ct+=1
					current += safe_division(curravg, avg_ct)

		# radio =  modem
		elif comp_name == "radio":
			#radio.on
			if "phone_scanning" in  bt_event.updates:
				# radio.scanning
				current += possible_states["scanning"] if "scanning" in possible_states else 0

			elif "mobile_radio" in  bt_event.updates:
				on_vals =  list(possible_states["on"]) if "on" in possible_states else []
				signal_stren = bt_event.updates["phone_signal_strength"] if "phone_signal_strength" in bt_event.updates else 0
				if signal_stren > len(on_vals) and len(on_vals)>0:
					 current+= on_vals[-1]
				elif len(on_vals)>0:
					current+= on_vals[signal_stren]
				# radio.active == mobile_radio - transmiting
				
		elif comp_name == "modem":
			#same as radio
			if "phone_scanning" in  bt_event.updates:
				curravg=0
				avg_ct=0
				if "tx" in possible_states["controller"]:
					on_vals =  possible_states["controller"]["tx"] if "tx" in possible_states["controller"] else [] 
					signal_stren = bt_event.updates["phone_signal_strength"] if "phone_signal_strength" in bt_event.updates else 0
					if signal_stren > len(on_vals) and len(on_vals)>0:
						curravg+= on_vals[-1]
					elif  len(on_vals)>0:
						curravg+= on_vals[signal_stren]

					avg_ct+=1
				if "rx" in possible_states["controller"]:
					curravg+=possible_states["controller"]["rx"]
					avg_ct+=1
				current += safe_division(curravg, avg_ct)
			elif "mobile_radio" in  bt_event.updates:
				current+=  possible_states["idle"] if "idle" in possible_states else 0	
		# cpu
		elif comp_name == "cpu":
			# retrieve just the component state
			#if phone has multiple cpu_clusters and that info is present in power profile file
			# only for devices with heterogeneous CPU architectures.
			#print(possible_states)
			#has_multiple_cpu_clusters= "clusters" in possible_states and "cores" in possible_states["clusters"] and  len(possible_states["clusters"]["cores"])>1
			#if has_multiple_cpu_clusters:
				#cores_per_cluster = possible_states["clusters"]["cores"]
				# calculate energy per cluster
				#if areInMinCPUFreq(bt_event.updates["cpufreq"] , possible_states):
						# assume is just awake

			#		current += possible_states["awake"]
		#		else:

					# calculate active state
		#			current += 0 # possible_states["awake"] if "awake" in possible_states else 0
		#			print("TODO Calculate power according to freq")
				


		#	else:
				if "running" in bt_event.updates:
					# is active or just awake	
					#if "awake" in possible_states and areInMinCPUFreq(bt_event.updates["cpufreq"] , possible_states):
					#if areInMinCPUFreq(bt_event.updates["cpufreq"] , possible_states):
						# assume is just awake

					#	current += possible_states["awake"]
					#else:
						# calculate active state
					#	current += 0 # possible_states["awake"] if "awake" in possible_states else 0
					#	print("TODO Calculate power according to freq")
					current = "active"
				else:
					#cpu in idle state
					#current+= possible_states["idle"] if "idle" in possible_states else 0
					current = "idle"

		return current

	def parseFile(self,filename):
		with open(filename, 'r') as filehandle:
			lines=filehandle.read().splitlines()
			self.parseHistory(lines)

#if __name__ == '__main__':
	#if len(sys.argv)>1:
		#pp = "samples/profiles/power_profile.xml"
		#pp = "samples/profiles/power_profile_pixel3a_grapheneos.xml"
		#x = BatteryStatsParser(powerProfile=pp,timezone="WET")
		#x.parseFile(sys.argv[1])
		

