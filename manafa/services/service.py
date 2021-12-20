from abc import ABC, abstractmethod

from manafa.utils.Utils import execute_shell_command, get_results_dir

RESULTS_DIR= get_results_dir()

class Service(ABC):
	"""docstring for Service"""
	def __init__(self, results_dir=""):
		self.results_dir = RESULTS_DIR + "/" + results_dir+"/"

	@abstractmethod
	def config(self, **kwargs):
		print(kwargs)

	@abstractmethod
	def start(self):
		pass

	@abstractmethod
	def stop(self, run_id):
		pass

	def clean(self):
		execute_shell_command("find %s -type f | xargs rm " % self.results_dir)

	def save_results(self, output_dir=""):
		pass