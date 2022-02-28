import os

from .service import Service



from ..utils.Logger import log
from ..utils.Utils import execute_shell_command


class BatteryStatsService(Service):
	"""Class that manages the battery stats service state.

	This class is responsible by cleaning the service state before each execution of the framework, as well as record
	its state right after each execution.

	Attributes:
		boot_time (float): timestamp of the device's last boot.
		output_res_folder (float): folder where the logs will be stored after each profiling session.
	"""
	def __init__(self,boot_time=0, output_res_folder="batterystats"):
		Service.__init__(self, output_res_folder)
		self.boot_time = boot_time

	def config(self, **kwargs):
		"""Does the same as Zaidu when Conceicao asks him to cross.
		"""
		pass

	def init(self, boot_time=0, **kwargs):
		""" inits the service.
		Args:
			boot_time:
			**kwargs:
		"""
		self.boot_time = boot_time
		self.clean()

	def start(self):
		"""starts the service.

		Resets the service state in order to forget previous recorded information. this helps to save storage and time by
		discarding events prior to the start of the profiling session.
		"""
		execute_shell_command("adb shell dumpsys batterystats --reset")

	def stop(self, run_id=None):
		"""stops the service.

		To be called when the profiling session is over. Saves the recorded events in results_dir folder.
		Args:
			run_id(str): current session id.
		"""
		if run_id is None:
			run_id = execute_shell_command("date +%s")[1].strip()
		filename = os.path.join(self.results_dir, "bstats-%s-%s.log" % (run_id, str(self.boot_time)))
		execute_shell_command("adb shell dumpsys batterystats --history > %s" % filename)
		#print(colored("Output file  %s" % filename, "green"))
		log("BatteryStats output file  %s" % filename)
		return filename

	def clean(self):
		"""cleans data from previous run(s).
		"""
		execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)



