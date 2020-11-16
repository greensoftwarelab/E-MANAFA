
from services.service import * 
from services.perfettoService import PerfettoService
from services.batteryStatsService import BatteryStatsService

from batteryStats.BatteryStatsParser import BatteryStatsParser
import time

DEFAULT_PROFILE="samples/profiles/power_profile.xml"

class GreenStats(Service):
	"""docstring for GreenStats"""
	def __init__(self,power_profile):
		Service.__init__(self)
		self.batterystats = BatteryStatsService()
		self.perfetto = PerfettoService()
		self.timezone = "WET"

	def init(self):
		self.batterystats.init()
		self.perfetto.init()
		
	def start(self):
		self.batterystats.start()
		self.perfetto.start()

	def stop(self):
		self.batterystats.stop()
		self.perfetto.stop()

	def clean(self):
		self.batterystats.clean()
		self.perfetto.clean()

	def parseResults(self,pp_file="", bts_file=""):
		bt_parser =  BatteryStatsParser(powerProfile=pp_file,timezone=self.timezone)
		bt_parser.parseFile(bts_file)

if __name__ == '__main__':
	print("ai")
	g = GreenStats(power_profile=DEFAULT_PROFILE)
	g.init()
	g.start()
	time.sleep(10)
	g.stop()









