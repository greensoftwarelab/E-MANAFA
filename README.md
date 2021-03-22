[![Build Status](https://travis-ci.com/RRua/e-manafa.svg?branch=main)](https://travis-ci.com/RRua/e-manafa)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/manafa.svg)](https://badge.fury.io/py/manafa)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/manafa)
[![PyPI status](https://img.shields.io/pypi/status/ansicolortags.svg)](https://pypi.python.org/pypi/manafa)
# E-MANAFA: Energy Monitor and ANAlyzer For Android

E-MANAFA is a software model-based tool for performing fine-grained estimates of energy consumption on Android devices. For this purpose, it uses values from power_profile.xml and from the BatteryStats and Perfetto services to estimate the energy consumption of each resource / component of the device. 


# SETUP

In order to run this tool, the following resources are required:
- A rooted Android device (running Android 9 or above);
- A *nix-based environment (MAC OS , Linux);
- Python 3.6 or above;
- Android Sdk tools (https://developer.android.com/studio/releases/platform-tools)

# Installation

```
pip install manafa
```

## define environment variables

In order to run this tool, there are at least 2 env. variables that need to be defined in the shell startup script (e.g .bashrc or .bash_profile file)

```
export ANDROID_HOME=$HOME/<your-android-instalation-folder>/ 
export PATH=$ANDROID_HOME/platform-tools:$PATH
```
## Replicate the environment

Install virtual virtualenv enviroment  (via python-pip):
```
$ python -m pip install --user virtualenv
```
## Replicate locally the dev virtualenv

```
$ virtualenv env/
```
## Activate the virtual environment
```
$ source env/bin/activate
```

## Extract power_profile.xml file from device (https://source.android.com/devices/tech/power/values)
Note: This file present in every device since Android 5 should contain values that were estimated by device manufacturers using external apparatus. However, most 
devices don't provide a fine-grained power profile. Google provides a set of instructions in order to complete this file with more accurate values(https://source.android.com/devices/tech/power/component).

```
TODO

```
# Install required packages
```
$ pip install -r requirements.txt

```
# Examples
```
# getting the energy consumed during a profiling session (between first and last measurement)
g = GreenStats(power_profile=DEFAULT_PROFILE, timezone="EST")
g.init()
g.start()
do_some_work()
batstats_out_file, perfetto_out_file = g.stop()
g.parseResults( DEFAULT_PROFILE, batstats_out_file , perfetto_out_file )
begin = g.bat_events.events[0].time
end = g.bat_events.events[-1].time
consumption,per_component_consumption = g.getConsumptionInBetween(begin, end)
print("Energy consumed: %f Joules" % consumption)
```

# Supported devices:
This tool can be used with any Android device able to run Perfetto, that is available since Android 9 (P). The tool so far was successfuly executed on the following devices:
- Pixel 3a
- Pixel 4a 5G
- Xiaomi Mi 9 Lite

# TODO
- calibrate the model
- test using flashlight
- wifi pixel4a
