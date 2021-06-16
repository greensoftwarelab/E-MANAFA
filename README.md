[![Build Status](https://travis-ci.com/RRua/e-manafa.svg?branch=main)](https://travis-ci.com/RRua/e-manafa)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/manafa.svg)](https://badge.fury.io/py/manafa)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/manafa)
[![PyPI status](https://img.shields.io/pypi/status/ansicolortags.svg)](https://pypi.python.org/pypi/manafa)
# E-MANAFA: Energy Monitor and ANAlyzer For Android

E-MANAFA is a plug-and-play software model-based tool for performing fine-grained estimates of energy consumption on Android devices. E-Manafa estimates system-level  and per-component energy consumption, by extracting information from the following sources:

- power_profile.xml: Device-specific file provided by manufacturers containing current consumption per component state;
- batterystats: Tool from Android framework that logs each power-related event that occurs between device charges;
- Perfetto: System-wide profiling for Linux and Android, that profiles high-frequency data, such as CPU frequency.

Note: Manufacturers not always supply information about the current consumed by an individual component in the power profile file. Use this information if it accurately represents the current drawn from the device battery in practice. The file can also be derived using external apparatus such as Monsoon. Google provides a set of guidelines to estimating the current of each component (https://source.android.com/devices/tech/power/component)

# SETUP

In order to run this tool, the following resources are required:
- rooted Android device (running Android 9 or above);
- *nix-based environment (MAC OS , Linux);
- Python 3.6 or above;
- Android Sdk tools (https://developer.android.com/studio/releases/platform-tools)

# Installation

## 1. Via python-pip

```
pip install manafa
```

### 1.1 define environment variables

In order to run this tool, there are at least 2 env. variables that need to be defined in the shell startup script (e.g .bashrc or .bash_profile file)

```
export ANDROID_HOME=$HOME/<your-android-instalation-folder>/ 
export PATH=$ANDROID_HOME/platform-tools:$PATH
```

## 2. From sources

### 2.1 Clone repo

```
$ git clone https://github.com/RRua/e-manafa.git
```

### 2.2 Replicate the environment

Install virtual virtualenv enviroment  (via python-pip):
```
$ python -m pip install --user virtualenv
```
### 2.3 Replicate locally the dev virtualenv

```
$ virtualenv env/
```

### 2.4 Activate the virtual environment
```
$ source env/bin/activate
```

### 2.6 Install required packages
```
$ pip install -r requirements.txt

```
### 2.6 define environment variables

In order to run this tool, there are at least 2 env. variables that need to be defined in the shell startup script (e.g .bashrc or .bash_profile file)

```
export ANDROID_HOME=$HOME/<your-android-instalation-folder>/ 
export PATH=$ANDROID_HOME/platform-tools:$PATH
```
# Usage

## Command line

```
$ python emanafa.py [-p|--profile <prof>] 
            [-t|--timezone <tz>] 
            [-pft|--perfettofile <pf>] 
            [-bts|--batstatsfile <bf>] 
```

## Source

```
# Example 
em = EManafa()
em.init()
em.start()
do_work_to_profile() # replace by procedure to be measured 
em.stop()
em.parseResults()
begin = em.bat_events.events[0].time  # first collected sample from batterystats
end = em.bat_events.events[-1].time  # last collected sample from batterystats
p, c, z = em.getConsumptionInBetween(begin, end)
print(f"TOTAL: {p} Joules")
```

# Supported devices:
This tool can be used with any Android device able to run Perfetto, available since Android 9 (P). The tool so far was successfuly executed on the following devices:
- Pixel 3a
- Pixel 4a 5G
- Xiaomi Mi 9 Lite

# TODO
- support for memory power calculator (MemoryPowerCalculator is a new addition in 8.0, mainly to count the power consumption on DDR memory . formula: MemoryPower = (mAatRail_1 * timeMs_1 + mAatRail_2 * timeMs_2 +… + mAatRail_n * timeMs_n) / (1000 * 60 * 60) (mAatRail_n: is the power at the read/write rate level, timeMs_n: is the time at the mAatRail_n level))
- start perfetto with protobuf config file
