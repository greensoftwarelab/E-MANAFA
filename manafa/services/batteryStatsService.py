from .service import Service

import time
from termcolor import colored

from ..utils.Logger import log
from ..utils.Utils import execute_shell_command


class BatteryStatsService(Service):
	"""docstring for BatteryStatsService"""
	def __init__(self, output_res_folder="batterystats"):
		Service.__init__(self,output_res_folder)

	def config(self,**kwargs):
		pass

	def init(self,**kwargs):
		self.clean()

	def start(self):
		execute_shell_command("adb shell dumpsys batterystats --reset")

	def stop(self,fil=None):
		
		if fil is None:
			uid_file = execute_shell_command("date +%s")[1].strip()
		filename = self.results_dir + "/bstats-%s.log" % uid_file
		execute_shell_command("adb shell dumpsys batterystats --history > %s" % filename)
		#print(colored("Output file  %s" % filename, "green"))
		log("Output file  %s" % filename)
		return filename

	def clean(self):
		execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)



