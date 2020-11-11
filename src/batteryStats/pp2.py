
import os, sys

import xml.etree.ElementTree as ET


class PowerProfile(object):
	"""docstring for PowerProfile"""
	def __init__(self,filename):
		self.filename = filename
		self.components={}
		self.read_power_profile()

	def addComponent(self,component):
		if component.name in self.components:
			self.components[component.name].states =  merge_two_dicts( self.components[component.name].states , (component.states))
		else:
			self.components[component.name] = component
		
	def __str__(self):
		return str(self.components)

	def __repr__(self):
		return str(self)				

	def read_power_profile(self):
		try:
			tree = ET.parse(self.filename)
			root = tree.getroot()
		except Exception as e:
			print("Exception: {0}".format(e))
			return
		
		for child in root:
			if child.tag == "item":
				ll = child.attrib['name'].split(".")
				begin_d = self.components
				for at in ll:
					begin_d[at]={} if not at in begin_d else begin_d[at]
					last_b = begin_d
					begin_d = begin_d[at]
				last_b[at]=float(child.text)
			elif child.tag == "array":
				ll = child.attrib['name'].split(".")
				begin_d = self.components
				for at in ll:
					begin_d[at]={} if not at in begin_d else begin_d[at]
					last_b = begin_d
					begin_d = begin_d[at]
				last_b[at]=   map( lambda xxz : float(xxz.text), child.getchildren() )  

	def estimatePowerUsage(self,state):
		return 0.0


if __name__ == '__main__':
	if len(sys.argv)>1:
		power_profile=PowerProfile(sys.argv[1])
		print(power_profile)