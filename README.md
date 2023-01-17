[![Build Status](https://travis-ci.com/RRua/e-manafa.svg?branch=main)](https://travis-ci.com/RRua/e-manafa)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/manafa.svg)](https://badge.fury.io/py/manafa)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/manafa)
[![PyPI status](https://img.shields.io/pypi/status/ansicolortags.svg)](https://pypi.python.org/pypi/manafa)
[![DOI](https://zenodo.org/badge/459943164.svg)](https://zenodo.org/badge/latestdoi/459943164)


# E-MANAFA: Energy Monitor and ANAlyzer For Android

E-MANAFA is a plug-and-play software model-based tool for performing fine-grained estimates of energy consumption on Android devices. E-Manafa estimates system-level  and per-component energy consumption, by extracting information from the following sources:

- power_profile.xml: Device-specific file provided by manufacturers containing current consumption per component state;
- batterystats: Tool from Android framework that logs each power-related event that occurs between device charges;
- Perfetto: System-wide profiling for Linux and Android, that profiles high-frequency data, such as CPU frequency.

Note: Manufacturers not always supply information about the current consumed by an individual component in the power profile file. Use this information if it accurately represents the current drawn from the device battery in practice. The file can also be derived using external apparatus such as Monsoon. Google provides a set of guidelines to estimating the current of each component (https://source.android.com/devices/tech/power/component)

## Documentation

https://greensoftwarelab.github.io/E-MANAFA/modules.html

## SETUP

In order to run this tool, the following resources are required:
- rooted Android device (running Android 9 or above);
- *nix-based environment (MAC OS, Linux);
- Python 3.6 or above;
- Android Sdk tools (https://developer.android.com/studio/releases/platform-tools)

## Installation

### 1. Via python-pip

```
pip install manafa
```

#### 1.1 define environment variables

In order to run this tool, there are at least 2 env. variables that need to be defined in the shell startup script (e.g .bashrc or .bash_profile file)

```
export ANDROID_HOME=$HOME/<your-android-instalation-folder>/ 
export PATH=$ANDROID_HOME/platform-tools:$PATH
```

### 2. From sources

#### 2.1 Clone repo

```
$ git clone https://github.com/greensoftwarelab/E-MANAFA.git
```

#### 2.2 Replicate the environment

Install virtual virtualenv enviroment  (via python-pip):
```
$ python -m pip install --user virtualenv
```
#### 2.3 Replicate locally the dev virtualenv

```
$ virtualenv env/
```

#### 2.4 Activate the virtual environment
```
$ source env/bin/activate
```

#### 2.5 Install required packages
```
$ pip install -r requirements.txt

```
#### 2.6 define environment variables

In order to run this tool, there are at least 2 env. variables that need to be defined in the shell startup script (e.g .bashrc or .bash_profile file)

```
export ANDROID_HOME=$HOME/<your-android-instalation-folder>/ 
export PATH=$ANDROID_HOME/platform-tools:$PATH
```
## Usage

### Command line

```
$ emanafa [-p|--profile <prof>] 
          [-t|--timezone <tz>] 
          [-pft|--perfettofile <pf>] 
          [-bts|--batstatsfile <bf>] 
```

### From project's root

```
$ python3 manafa/main.py [-p|--profile <prof>] 
                     [-t|--timezone <tz>] 
                     [-pft|--perfettofile <pf>] 
                     [-bts|--batstatsfile <bf>] 
```

### Source

```
# Example 
em = EManafa()
em.init()
em.start()
do_work_to_profile() # e.g time.sleep(10)
em.stop()
em.parse_results()
begin = manafa.perf_events.events[0].time  # first sample from perfetto
end = manafa.perf_events.events[-1].time  # last sample from perfetto
p, c, z = em.get_consumption_in_between(begin, end)
out_file = em.save_final_report(begin)
print(f"TOTAL: {p} Joules")
```
## Associated publications:

```
@inproceedings{
          10.1145/3551349.3561342,
          author = {Rua, Rui and Saraiva, Jo\~{a}o},
          title = {E-MANAFA: Energy Monitoring and ANAlysis Tool For Android},
          year = {2023},
          isbn = {9781450394758},
          publisher = {Association for Computing Machinery},
          address = {New York, NY, USA},
          url = {https://doi.org/10.1145/3551349.3561342},
          doi = {10.1145/3551349.3561342},
          articleno = {202},
          numpages = {4},
          location = {Rochester, MI, USA},
          series = {ASE22}
}
```
