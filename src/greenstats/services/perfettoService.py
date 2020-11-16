
from __future__ import absolute_import

from .service import Service
from .utils import executeShCommand 
import time

class PerfettoService(Service):
	"""docstring for BatteryStatsService"""
	def __init__(self,output_res_folder="batterystats"):
		Service.__init__(self,output_res_folder)
		
	def init(self,**kwargs):
		self.clean()
	def start(self):
		executeShCommand("adb shell perfetto -o /data/misc/perfetto-traces/trace freq -t 1h --background ")
	def stop(self):
		executeShCommand("adb shell su -c \"killall perfetto\"")
		executeShCommand("adb pull /data/misc/perfetto-traces/trace " + ("%strace" % self.results_dir )   +"-$(date +%s)")
		self.export()
	
	def export(self):
		pass


	def clean(self):
		executeShCommand("find %s -type f -name \"perfettotrace*\" | xargs rm " % self.results_dir)


