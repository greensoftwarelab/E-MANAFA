import time

from manafa.services.batteryStatsService import BatteryStatsService
from manafa.services.service import *
from manafa.services.perfettoService import PerfettoService
from manafa.perfetto.perfettoParser import PerfettoCPUfreqParser
from manafa.batteryStats.BatteryStatsParser import BatteryStatsParser
import argparse
from manafa.utils.Logger import log, LogSeverity
from manafa.utils.Utils import execute_shell_command, mega_find

DEFAULT_PROFILE="resources/profiles/power_profile.xml"
DEFAULT_TIMEZONE="GMT"

def getLastBootTime(bts_file=None):
	res, out, err = execute_shell_command("adb shell cat /proc/stat | grep btime | awk '{print $2}'") #executeShCommand("adb shell cat /proc/stat | grep btime | awk '{print $2}'")
	if res != 0 or len(out) == 0:
		log("no device connected. Assuming Boot time of battery stats file", LogSeverity.ERROR)
		flds = bts_file.split("-") if bts_file is not None else []
		if len(flds)>1:
			log("Boot time: " + flds[2], LogSeverity.WARNING )
			return int(flds[2])
		else:
			log("no device connected. Assuming Boot time 0", LogSeverity.WARNING)
			return 0
			#raise Exception("Invalid boot time ")
		#print("[Warning]: no device connected. Assuming Boot time %d" % boot_time)
	return float(out.strip())

def is_float(string):
	try:
		float(string)
	except ValueError:
		return False
	return True

class EManafa(Service):
	"""docstring for GreenStats"""
	def __init__(self, power_profile, timezone="EST", resources_dir="resources"):
		Service.__init__(self)
		self.power_profile = power_profile
		self.boot_time = 0
		log("Power profile file: " + power_profile , LogSeverity.INFO )
		self.resources_dir = resources_dir
		self.batterystats = BatteryStatsService()
		self.perf_events = None
		self.perfetto = PerfettoService()
		self.timezone = timezone

	def config(self, **kwargs):
		pass

	def init(self):
		self.boot_time = getLastBootTime()
		self.batterystats.init(boot_time = self.boot_time)
		self.perfetto.init(boot_time = self.boot_time)
		
	def start(self):
		self.batterystats.start()
		self.perfetto.start()

	def stop(self):
		b_out = self.batterystats.stop()
		p_out = self.perfetto.stop()
		return b_out, p_out
	
	def clean(self):
		self.batterystats.clean()
		self.perfetto.clean()

	def parseResults(self, bts_file="", pf_file=""):
		if bts_file== "" or pf_file == "":
			log("Empty result files", LogSeverity.FATAL)
			raise Exception()
		self.b_time = getLastBootTime(bts_file)
		self.bat_events = BatteryStatsParser(self.power_profile, timezone=self.timezone)
		self.bat_events.parseFile(bts_file)
		self.perf_events = PerfettoCPUfreqParser(self.power_profile, self.b_time, timezone=self.timezone)
		self.perf_events.parseFile(pf_file)

	# energy calc related stuff
	def getConsumptionInBetween(self, start_time=0, end_time=9905715380):
		total, per_component = self.calculateNonCpuEnergy(start_time, end_time)
		total_cpu = self.calculateCPUEnergy(start_time,end_time)
		per_component['cpu'] += total_cpu
		return total + total_cpu, per_component

	def calculateNonCpuEnergy(self, start_time, end_time):
		c_beg_bef, c_beg_aft = getClosestPair(self.bat_events.events, start_time)
		total = 0
		per_component_consumption = {}
		last_event = self.bat_events.events[c_beg_bef]
		last_time = start_time
		for i, x in enumerate(self.bat_events.events[c_beg_aft:]):
			if x.time > end_time:
				break
			delta_time = abs(x.time - last_time)
			tot_curr, comps_curr = last_event.getCurrentOfBatStatEvent()
			total += tot_curr * (last_event.getVoltageValue()) * delta_time
			for comp, comp_curr in comps_curr.items():
				if comp not in per_component_consumption:
					per_component_consumption[comp] = 0
				if is_float(comp_curr):
					per_component_consumption[comp] += (comp_curr * last_event.getVoltageValue() * delta_time)
			last_event = x
			last_time = x.time

		delta_time = end_time - last_time 
		if delta_time < 0.0:
			log(time.time(), "Error calculating delta (<0) ", LogSeverity.FATAL)
		tot_curr, comps_curr = last_event.getCurrentOfBatStatEvent()
		total += tot_curr * (last_event.getVoltageValue()) * (delta_time)
		for comp, comp_curr in comps_curr.items():
			if comp not in per_component_consumption:
				per_component_consumption[comp] = 0
			if is_float(comp_curr):
				per_component_consumption[comp] += (comp_curr * last_event.getVoltageValue() * delta_time)
		return total, per_component_consumption


	def calculateCPUEnergy(self,start_time,end_time):
		c_beg_bef,c_beg_aft =  getClosestPair(self.perf_events.events, start_time)
		#c_end_bef,c_end_aft =  getClosestPair(self.perf_events.events, end_time)
		total = 0
		last_event = self.perf_events.events[c_beg_bef]
		last_time = start_time
		tot_time=0
		for i, x in enumerate(self.perf_events.events[c_beg_aft:]):
			if x.time > end_time:
				break
			#print("between %f - %f" %(last_time,x.time) )
			# get different states of cpu btween perf event interval
			#print( x.time - last_time )
			l = self.bat_events.getCPUSamplesInBetween(last_time,x.time)
			# TODO : test to assert if x.time - last_time  = sum( deltas_of_L )
			for sample in l:
				delta, state, voltage = sample[0],sample[1],sample[2]
				cpus_current = last_event.calculateCPUsCurrent(state, self.perf_events.power_profile)
				tot_time += delta
				total += ( cpus_current) * delta * voltage
			last_event = x 
			last_time = x.time
		
		# after calcs'''
		# TODO merge with cycle just like with non cpu
		l = self.bat_events.getCPUSamplesInBetween(last_time, end_time)
		for sample in l:
			delta, state, voltage = sample[0], sample[1], sample[2]
			cpus_current = last_event.calculateCPUsCurrent(state, self.perf_events.power_profile)
			tot_time += delta
			total += (cpus_current) * delta * voltage
		# TODO just like non cpu
		#print(tot_time)
		return total
		

def getClosestPair(events, time):
	lasti = 0
	for i, x in enumerate(events):
		if x.time>time:
			return lasti, i	
		lasti = i
	return lasti,lasti


def extractPowerProfile(resources_dir, filename):
	# extracting power_profile.xml from device
	res, suc, _ = execute_shell_command("adb pull /system/framework/framework-res.apk %s" % resources_dir)
	if res==0:
		cmd = """java -jar {res_dir}/apktool_2.4.0.jar d -s {res_dir}/framework-res.apk -o {res_dir}/out_jar_dir/""".format(res_dir=resources_dir)
		res, suc, _ = execute_shell_command(cmd)
		pp_file = resources_dir + "/out_jar_dir/res/xml/power_profile.xml"
		if res==0:
			# cp to profiles, remove out_jar_dir and framework-res.apk
			res,_,_=  execute_shell_command("cp {extracted_file} \"{res_dir}/profiles/{new_file}\" ; rm -rf {res_dir}/out_jar_dir {res_dir}/framework-res.apk".format(extracted_file=pp_file, new_file=filename, res_dir=resources_dir ))
			if res ==0:
				return filename

	return DEFAULT_PROFILE

def inferPowerProfile(resources_dir):
	res, device_model, _ = execute_shell_command("adb shell getprop ro.product.model")
	if res == 0 and device_model != "":
		model_profile_file = """power_profile_{device_model}.xml""".format(device_model=device_model.replace(" ", "").strip().lower())
		matching_profiles = mega_find(resources_dir, pattern=model_profile_file, maxdepth=2)
		if len(matching_profiles) > 0:
			return matching_profiles[0]
		else:
			# if power profile not present in profiles directory, extract from device
			power_profile = extractPowerProfile(resources_dir,model_profile_file)
			return power_profile
	else:
		return DEFAULT_PROFILE

def inferTimezone():
	res,out,err = execute_shell_command("adb shell date")
	default_tz = DEFAULT_TIMEZONE
	if res == 0 and len(out) > 0:
		default_tz = out.split(" ")[-2]
	log("Using timezone: %s" % default_tz)
	return default_tz


if __name__ == '__main__':
	default_resources_dir = "resources"
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--profile", default=inferPowerProfile(default_resources_dir), type=str)
	parser.add_argument("-t", "--timezone", default=inferTimezone(), type=str)
	args = parser.parse_args()
	g = EManafa(power_profile=args.profile, timezone=args.timezone,resources_dir=default_resources_dir)
	g.init()
	g.start()
	time.sleep(7) # do work
	bts_file, pf_file = g.stop()
	#bts_file = "results/batterystats/bstats-1615831762.log"
	#pf_file = "results/perfetto/trace-1615831762.systrace"
	g.parseResults(bts_file, pf_file )
	begin = g.bat_events.events[0].time
	end = g.bat_events.events[-1].time
	consumption, per_component_consumption = g.getConsumptionInBetween(begin, end)
	print(per_component_consumption)
	log("Energy consumed: %f Joules" % consumption, log_sev=LogSeverity.SUCCESS)

