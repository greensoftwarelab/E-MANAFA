

import re


class PerfettoEvent(object):
	"""docstring for BatteryEvent"""
	def __init__(self,time=0.0,values=[]):
		self.time=time
		self.vals=[]
		for x in values:
			self.vals.append(x)

	def __str__(self):
		return "time:%f vals =  %s , " % (self.time,str(self.vals))

	def __repr__(self):
		return str(self)

	def initAll(self,default_len=8,val=0):
		for x in xrange(0,default_len):
			if len(self.vals)> x :
				self.vals[x]=val 
			else: 
				self.vals.append(val)

	def update(self, cpu_id,cpu_freq):
		if len(self.vals)> cpu_id:
			self.vals[cpu_id]=cpu_freq 
		else: 
			for x in xrange(len(self.vals)-1,cpu_id ):
				self.vals.append( cpu_freq)



class PerfettoCPUfreqParser(object):
	def __init__(self,start_time=0.0,timezone="EST"):
		self.events = []
		self.start_time = start_time
	
	def parseFile(self,filename):
		with open(filename, 'r') as filehandle:
			lines=filehandle.read().splitlines()
			self.parseHistory(lines)

	def parseHistory(self,lines):
		for line in lines:
			if line.startswith("#"):
				continue
			z =  re.match(r"^\s*([^\s]+)\-(\d+)\s*\(\s*(\d+|\-+)\) \[(\d+)\] (\d+|\.+) ([0-9]*\.[0-9]+|[0-9]+)\: (.*)?$",line)
			if z: 
				time = float (z.groups()[5])
				time += self.start_time
				cpu_id,cpu_freq = self.parseEvent(z.groups()[6])
				self.addEvent(time,cpu_id,cpu_freq)
			else:
				raise Exception ("Error parsing file")
		
	def addEvent(self,time,cpu_id,cpu_freq):
		if len(self.events)==0:
			z = PerfettoEvent(time)
			z.initAll(default_len=6,val=cpu_freq)
			self.events.append(z)
		else:
			last = self.events[-1]
			z = PerfettoEvent(time, last.vals)
			z.update(cpu_id,cpu_freq)
			self.events.append(z)

	def parseEvent(self, ev_str):
		mat = re.match (r"cpu_frequency: state=(\d+) cpu_id=(\d+)", ev_str)
		if mat:
			cpu_id=int(mat.groups()[1])
			cpu_freq=int(mat.groups()[0])
			return cpu_id,cpu_freq
		

bootTime = 1605110840
x = PerfettoCPUfreqParser(bootTime)
x.parseFile("/Users/ruirua/repos/petra_like/out.systrace")
print(x.events)

