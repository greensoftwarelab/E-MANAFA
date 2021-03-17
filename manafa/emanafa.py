import time

from manafa.services.batteryStatsService import BatteryStatsService
from manafa.services.service import *
from manafa.services.perfettoService import PerfettoService
from manafa.perfetto.perfettoParser import PerfettoCPUfreqParser
from manafa.batteryStats.BatteryStatsParser import BatteryStatsParser
import argparse
from manafa.utils.Logger import log, LogSeverity

#DEFAULT_PROFILE="samples/profiles/power_profile.xml"
#DEFAULT_PROFILE="samples/profiles/power_profile_pixel3a_grapheneos.xml"
from manafa.utils.Utils import execute_shell_command

DEFAULT_PROFILE="resources/profiles/power_profile_pixel4a_grapheneos.xml"
DEFAULT_TIMEZONE="GMT"

def getLastBootTime():
	res,out,err = execute_shell_command("adb shell cat /proc/stat | grep btime | awk '{print $2}'") #executeShCommand("adb shell cat /proc/stat | grep btime | awk '{print $2}'")
	if res !=0 or len(out) == 0:
		boot_time = 1605110840
		log( "no device connected. Assuming Boot time %d" % boot_time, LogSeverity.ERROR )
		#print("[Warning]: no device connected. Assuming Boot time %d" % boot_time)
		return boot_time
	return float(out.strip())


class EManafa(Service):
	"""docstring for GreenStats"""
	def __init__(self,power_profile,timezone="EST"):
		Service.__init__(self)
		self.batterystats = BatteryStatsService()
		self.bat_events = None
		self.perf_events = None
		self.perfetto = PerfettoService()
		self.timezone = timezone

	def config(self,**kwargs):
		pass

	def init(self):
		self.batterystats.init()
		self.perfetto.init()
		
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

	def parseResults(self, pp_file=DEFAULT_PROFILE, bts_file="", pf_file=""):
		if bts_file== "" or pf_file == "":
			log("Empty result files", LogSeverity.FATAL)
			raise Exception()
		self.bat_events = BatteryStatsParser(powerProfile=pp_file, timezone=self.timezone)
		self.bat_events.parseFile(bts_file)
		b_time = getLastBootTime()
		self.perf_events = PerfettoCPUfreqParser(pp_file, b_time, timezone=self.timezone)
		self.perf_events.parseFile(pf_file)
	

	# energy calc related stuff
	def getConsumptionInBetween(self,start_time=0, end_time=9905715380):
		return self.calculateNonCpuEnergy(start_time, end_time)  \
			+ self.calculateCPUEnergy(start_time, end_time)

	def calculateNonCpuEnergy(self, start_time, end_time):
		c_beg_bef, c_beg_aft = getClosestPair(self.bat_events.events, start_time)
		total = 0
		last_event = self.bat_events.events[c_beg_bef]
		last_time = start_time
		for i, x in enumerate(self.bat_events.events[c_beg_aft:]):
			if x.time > end_time:
				break
			delta_time = abs(x.time - last_time)
			total += last_event.getCurrentOfBatStatEvent() * (last_event.getVoltageValue()) * (delta_time)
			last_event = x
			last_time = x.time

		delta_time = end_time - last_time 
		if delta_time < 0.0:
			log(time.time(), "Error calculating delta (<0) ", LogSeverity.FATAL )
			print("fatal error")
		total += last_event.getCurrentOfBatStatEvent() * (last_event.getVoltageValue()) * (delta_time)
		
		return total


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
				delta,state,voltage = sample[0],sample[1],sample[2]
				cpus_current= last_event.calculateCPUsCurrent(state,self.perf_events.power_profile)
				tot_time +=delta
				total += ( cpus_current) * delta * voltage
			last_event = x 
			last_time = x.time
		
		# after calcs'''
		# TODO merge with cycle just like with non cpu
		l = self.bat_events.getCPUSamplesInBetween(last_time,end_time)
		for sample in l:
			delta,state,voltage = sample[0],sample[1],sample[2]
			cpus_current= last_event.calculateCPUsCurrent(state,self.perf_events.power_profile) 
			#print("cpucu- "+str(cpus_current))
			#print("delta- "+str(delta))
			#print("volta- "+str(voltage))
			tot_time +=delta
			total += ( cpus_current) *  delta * voltage 
			#print("total- " + str(total))
			#print()
			
		# TODO just like non cpu
		#print(tot_time)
		return total
		

def getClosestPair(events, time ):
	lasti = 0
	for i, x in enumerate(events):
		if x.time>time:
			return lasti, i	
		lasti = i
	return lasti,lasti

def inferPowerProfile():
	return DEFAULT_PROFILE#TODO

def inferTimezone():
	res,out,err = execute_shell_command("adb shell date")
	default_tz = DEFAULT_TIMEZONE
	if res ==0 and len(out)>0:
		default_tz = out.split(" ")[-2]
	log("Using timezone: %s" % default_tz)
	return default_tz

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--profile", default=inferPowerProfile(), type=str)
	parser.add_argument("-t", "--timezone", default=inferTimezone(), type=str)
	args = parser.parse_args()
	g = EManafa(power_profile=args.profile, timezone=args.timezone)
	g.init()
	g.start()
	time.sleep(7)# do work
	bts_file, pf_file = g.stop()
	#bts_file = "results/batterystats/bstats-1615831762.log"
	#pf_file = "results/perfetto/trace-1615831762.systrace"
	g.parseResults(DEFAULT_PROFILE, bts_file , pf_file )
	begin = g.bat_events.events[0].time
	end = g.bat_events.events[-1].time
	consumption = g.getConsumptionInBetween(begin, end)
	log("Energy consumed: %f Joules" % consumption, log_sev=LogSeverity.SUCCESS)


