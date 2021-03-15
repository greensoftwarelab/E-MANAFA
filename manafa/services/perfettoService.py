
from __future__ import absolute_import

from .service import Service
import time
import os

from manafa.utils.Utils import execute_shell_command


class PerfettoService(Service):
	"""docstring for BatteryStatsService"""
	def __init__(self,output_res_folder="perfetto"):
		Service.__init__(self,output_res_folder)

	def config(self,**kwargs):
		pass

	def init(self,**kwargs):
		self.clean()

	def start(self):
		execute_shell_command("adb shell perfetto -o /data/misc/perfetto-traces/trace freq  -t 1h --background ")
	
	def stop(self,file_id=None):
		if file_id is None:
			file_id = execute_shell_command("date +%s")[1].strip()
		#executeShCommand("adb shell su -c \"killall perfetto\"")
		execute_shell_command("adb shell killall perfetto")
		time.sleep(1)
		execute_shell_command("adb pull /data/misc/perfetto-traces/trace " + ("%strace" % self.results_dir )   +"-"+file_id)
		return self.export()
	
	
	def export(self):
		last_exported = ""
		for f in os.listdir(self.results_dir):
			execute_shell_command("./resources/traceconv systrace %s/%s %s/%s.systrace" %(self.results_dir,f,self.results_dir,f) )
			last_exported = "%s/%s.systrace" %(self.results_dir,f)
		return last_exported
	def clean(self):
		execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)


