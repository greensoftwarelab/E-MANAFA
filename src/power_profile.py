
import os, sys

import xml.etree.ElementTree as ET


def merge_two_dicts(x, y):
	z = x.copy()   # start with x's keys and values
	z.update(y)    # modifies z with y's keys and values & returns None
	return z

class PowerState(object):
	"""docstring for State"""
	def __init__(self, state_name, state_values=[]  ):
		super(PowerState, self).__init__()
		self.name=state_name
		self.state_values = state_values

	def __str__(self):
		return str(self.name) + str(self.state_values)

	def __repr__(self):
		return str(self)	


class Component(object):
	"""docstring for Component"""
	def __init__(self, name, state_dict={}):
		super(Component, self).__init__()
		self.name = name
		self.states= state_dict

	def __str__(self):
		return "name:%s - states = " % self.name + str(self.states)

	def __repr__(self):
		return str(self)

	def addState(self,state):
		#if state.name in self.states:
			#self.states[state.name] = ( self.states[state.name] + (state.state_values))
		#else:
		self.states[state.name] = state.state_values

class PowerProfile(object):
	"""docstring for PowerProfile"""
	def __init__(self):
		super(PowerProfile, self).__init__()
		self.components={}



	def addComponent(self,component):
		if component.name in self.components:
			self.components[component.name].states =  merge_two_dicts( self.components[component.name].states , (component.states))
		else:
			self.components[component.name] = component
		
	#def getValue(component_name, state_name, )

	def __str__(self):
		return str(self.components)

	def __repr__(self):
		return str(self)				

def read_power_profile(filename):
	try:
		tree = ET.parse(filename)
		root = tree.getroot()
	except Exception as e:
		print("Exception: {0}".format(e))
		return
	pp = PowerProfile()
	for child in root:
		if child.tag == "item":
			ll = child.attrib['name'].split(".")
			if len(ll)>1:
				cp = Component(ll[0], {} )
				st = PowerState(ll[1], [float(child.text)] )
				cp.addState(st)
				pp.addComponent(cp)

		elif child.tag == "array":
			ll = child.attrib['name'].split(".")
			if len(ll)>1:
				cp = Component(ll[0], {} )
				state_list =  map( lambda xxz : float(xxz.text), child.getchildren() )  
				st = PowerState(state_name=ll[1], state_values=state_list)
				cp.addState(st)
				pp.addComponent(cp)
		
	return pp


if __name__ == '__main__':
	if len(sys.argv)>1:
		power_profile=read_power_profile(sys.argv[1])