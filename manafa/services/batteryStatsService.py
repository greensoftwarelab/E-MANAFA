from .service import Service



from ..utils.Logger import log
from ..utils.Utils import execute_shell_command


class BatteryStatsService(Service):
	"""docstring for BatteryStatsService"""
	def __init__(self,boot_time=0, output_res_folder="batterystats"):
		Service.__init__(self,output_res_folder)
		self.boot_time = boot_time

	def config(self,**kwargs):
		pass

	def init(self,boot_time=0,**kwargs):
		self.boot_time = boot_time
		self.clean()

	def start(self):
		execute_shell_command("adb shell dumpsys batterystats --reset")

	def stop(self, run_id=None):
		if run_id is None:
			run_id = execute_shell_command("date +%s")[1].strip()
		filename = self.results_dir + "/bstats-%s-%s.log" % (run_id, str(self.boot_time))
		execute_shell_command("adb shell dumpsys batterystats --history > %s" % filename)
		#print(colored("Output file  %s" % filename, "green"))
		log("Output file  %s" % filename)
		return filename

	def clean(self):
		execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)



