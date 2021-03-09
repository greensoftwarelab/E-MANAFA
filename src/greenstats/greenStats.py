
from services.service import * 
from services.perfettoService import PerfettoService
from services.batteryStatsService import BatteryStatsService
from services.utils import executeShCommand
from batteryStats.perfettoParser import PerfettoCPUfreqParser
from batteryStats.BatteryStatsParser import BatteryStatsParser

import time

#DEFAULT_PROFILE="samples/profiles/power_profile.xml"
DEFAULT_PROFILE="samples/profiles/power_profile_pixel3a_grapheneos.xml"


def getLastBootTime():
	x = executeShCommand("adb shell cat /proc/stat | grep btime | awk '{print $2}'")
	if x is None:
		boot_time = 1605110840
		return boot_time
		print("erro.dispositivo nao conectado")
	return float(x.strip())


class GreenStats(Service):
	"""docstring for GreenStats"""
	def __init__(self,power_profile,timezone="EST"):
		Service.__init__(self)
		self.batterystats = BatteryStatsService()
		self.bat_events = None
		self.perf_events = None
		self.perfetto = PerfettoService()
		self.timezone = timezone

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

	def parseResults(self,pp_file=DEFAULT_PROFILE, bts_file="",pf_file=""):
		self.bat_events = BatteryStatsParser(powerProfile=pp_file,timezone=self.timezone)
		self.bat_events.parseFile(bts_file)
		b_time = getLastBootTime()
		self.perf_events = PerfettoCPUfreqParser(pp_file,b_time,timezone=self.timezone)
		self.perf_events.parseFile(pf_file)
	

	# energy calc related stuff
	def getConsumptionInBetween(self,start_time=0, end_time=9905715380):
		return self.calculateNonCpuEnergy(start_time,end_time)  \
			+  self.calculateCPUEnergy(start_time,end_time)		

	def calculateNonCpuEnergy(self, start_time, end_time):
		c_beg_bef,c_beg_aft =  getClosestPair(self.bat_events.events, start_time)
		c_end_bef,c_end_aft =  getClosestPair(self.bat_events.events, end_time)
		total = 0
		last_event = self.bat_events.events[c_beg_bef]
		last_time = start_time
		for i, x in enumerate(self.bat_events.events[c_beg_aft:]):
			if x.time > end_time:
				break
			delta_time = abs (x.time - last_time)
			total += last_event.getCurrentOfBatStatEvent() * (last_event.getVoltageValue()) * (delta_time)
			#print(total)
			last_event = x
			last_time = x.time
		

		delta_time = end_time - last_time 
		if delta_time < 0.0:
			print("fatal error")
		total += last_event.getCurrentOfBatStatEvent() * (last_event.getVoltageValue()) * (delta_time)
		
		return total


	def calculateCPUEnergy(self,start_time,end_time):
		c_beg_bef,c_beg_aft =  getClosestPair(self.perf_events.events, start_time)
		c_end_bef,c_end_aft =  getClosestPair(self.perf_events.events, end_time)
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
				#print("cpucu- "+str(cpus_current))
				#print("delta- "+str(delta))
				#print("volta- "+str(voltage))
				tot_time +=delta
				total += ( cpus_current) *  delta * voltage 
				#print("total- " + str(total))
			last_event = x 
			last_time = x.time
		
		# after calcs'''
		# TODO merge with cycle
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

if __name__ == '__main__':
	g = GreenStats(power_profile=DEFAULT_PROFILE,timezone="EST")
	g.init()
	g.start()
	time.sleep(10) # do work 
	bts_file, pf_file =  g.stop()
	g.parseResults( DEFAULT_PROFILE, bts_file , pf_file )
	begin = g.bat_events.events[0].time
	end = g.bat_events.events[-1].time
	consumption = g.getConsumptionInBetween(begin, end)
	print("Energy consumed: %f Joules" % consumption)






