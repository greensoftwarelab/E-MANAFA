from .service import Service
from .utils import executeShCommand 
import time
from termcolor import colored

class BatteryStatsService(Service):
	"""docstring for BatteryStatsService"""
	def __init__(self, output_res_folder="batterystats"):
		Service.__init__(self,output_res_folder)
		
	def init(self,**kwargs):
		self.clean()

	def start(self):
		executeShCommand("adb shell dumpsys batterystats --reset")

	def stop(self,fil=None):
		
		if fil is None:
			uid_file = executeShCommand("date +%s").strip()
		filename = self.results_dir + "/bstats-%s.log" % uid_file
		executeShCommand("adb shell dumpsys batterystats --history > %s" % filename)
		print(colored("Output file  %s" % filename, "green"))
		return filename

	def clean(self):
		executeShCommand("find %s -type f  | xargs rm " % self.results_dir)



