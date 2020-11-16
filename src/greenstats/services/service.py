
RESULTS_DIR="results/"
from .utils import executeShCommand
class Service(object):
	"""docstring for Service"""
	def __init__(self,results_dir=""):
		self.results_dir = RESULTS_DIR + results_dir+"/"
	
	def config(self,**kwargs):
		print(kwargs)

	def start(self):
		pass

	def stop(self):
		pass

	def clean(self):
		executeShCommand("find %s -type f | xargs rm " % self.results_dir)
