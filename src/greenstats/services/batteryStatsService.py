from .service import Service
from .utils import executeShCommand 
import time
from termcolor import colored

class BatteryStatsService(Service):
	"""docstring for BatteryStatsService"""
	def __init__(self, output_res_folder="batterystats"):
		Service.__init__(self,output_res_folder)
		
	def init(self,**kwargs):
		pass
	def start(self):
		executeShCommand("adb shell dumpsys batterystats --reset")

	def stop(self):
		executeShCommand("adb shell dumpsys batterystats --history >" + self.results_dir+ "/-$(date +\"%s\").log")
		print(colored("Output file in %s" % self.results_dir, "green"))

