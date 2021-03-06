
import os, sys

import xml.etree.ElementTree as ET


class PowerProfile(object):
	"""Stores information regarding devices' power profile xml file.

	Stores information about the file and each  pair component, current contained in the file.
	Attributes:
		filename(str): path of power profile file.
	"""
	def __init__(self, filename):
		self.filename = filename
		self.components = {}
		self.__read_power_profile()
		#print(self.components)

	def add_component(self, component):
		"""adds component to current state.
		Args:
			component (dict): component info.
		"""
		if component.name in self.components:
			self.components[component.name].states = self.merge_two_dicts(self.components[component.name].states , (component.states))
		else:
			self.components[component.name] = component

	@staticmethod
	def merge_two_dicts(self: object, x: object, y: object) -> object:
		z = x.copy()
		z.update(y)
		return z

	def __str__(self) -> str:
		return str(self.components)

	def __repr__(self) -> str:
		return str(self)				

	def __read_power_profile(self):
		"""parses power profile xml file.
		"""
		try:
			tree = ET.parse(self.filename)
			root = tree.getroot()
		except Exception as e:
			print("Exception: {0}".format(e))
			return None
		
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
					begin_d[at]={} if at not in begin_d else begin_d[at]
					last_b = begin_d
					begin_d = begin_d[at]
				last_b[at] = list( map( lambda xxz : float(xxz.text),  list(child)))

	def get_CPU_state_current(self, state):
		"""retrieves the current consumed by cpu at a given state.
		Args:
			state: given state.

		Returns:
			current: the current being consumed.
		"""
		return self.components["cpu"][state] if state in self.components else self.components["cpu"]["active"]

	# returns pair with closest_val_before_freq,closest_val_after_freq
	def get_CPU_core_speed_pair(self, core_id, core_freq):
		"""retrieves a pair with the before and after closest frequency values for a core identified by core_id at a given frequency.

		Power profile file stores current values measured at specific fixed frequencies. Many times, a given core is running at a frequency
		different from the ones recorded in file. In order to estimate the current consumption at core_freq, there is need to  interpolate
		the closest recorded values.

		Args:
			core_id: core id.
			core_freq: core frequency.

		Returns:
			fst_pair: before value.
			snd_pair: after value.
		"""
		profile_speeds = self.components["cpu"]["speeds"] if "speeds" in self.components["cpu"]else self.components["cpu"]["core_speeds"]
		profile_currents = self.components["cpu"]["active"] if ("speeds" in self.components["cpu"] and isinstance(self.components["cpu"]["active"], list)) else self.components["cpu"]["core_power"]

		if isinstance(profile_speeds, dict):
			# select respective cluster of core_id	
			core_r = core_id + 1
			cluster_cores = self.components["cpu"]["clusters"]["cores"]
			for i, ncores in enumerate(cluster_cores):
				if core_r > ncores:
					core_r = core_r - ncores
				else:
					profile_speeds = self.components["cpu"]["core_speeds"]["cluster%d" % i]
					profile_currents = self.components["cpu"]["core_power"]["cluster%d" % i]
					break
		mini_fr = 0
		freq = 0
		# find adequate freq
		for i, f in enumerate(profile_speeds):
			if f >= core_freq:
				freq = i
				break
			mini_fr = i
		fst_pair = (profile_speeds[mini_fr], profile_currents[mini_fr])
		snd_pair = (profile_speeds[freq], profile_currents[freq])
		return fst_pair, snd_pair


if __name__ == '__main__':
	if len(sys.argv) > 1:
		power_profile = PowerProfile(sys.argv[1])
		print(power_profile)