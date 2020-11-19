
from __future__ import absolute_import

from .service import Service
from .utils import executeShCommand 
import time,os

class PerfettoService(Service):
	"""docstring for BatteryStatsService"""
	def __init__(self,output_res_folder="perfetto"):
		Service.__init__(self,output_res_folder)
		
	def init(self,**kwargs):
		self.clean()

	def start(self):
		executeShCommand("adb shell perfetto -o /data/misc/perfetto-traces/trace freq -t 1h --background ")
	
	def stop(self,file_id=None):
		if file_id is None:
			file_id = executeShCommand("date +%s").strip() 
		executeShCommand("adb shell su -c \"killall perfetto\"")
		executeShCommand("adb pull /data/misc/perfetto-traces/trace " + ("%strace" % self.results_dir )   +"-$(date +%s)")
		return self.export()
	
	def export(self):
		last_exported = ""
		for f in os.listdir(self.results_dir):
			executeShCommand("./resources/traceconv systrace %s/%s %s/%s.systrace" %(self.results_dir,f,self.results_dir,f) )
			last_exported=  "%s/%s.systrace" %(self.results_dir,f)
		return last_exported
	def clean(self):
		executeShCommand("find %s -type f  | xargs rm " % self.results_dir)


