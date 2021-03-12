# petra-like

This tool is a software model-based tool, for performing fine-grained estimates of energy consumption on Android devices. For this purpose, it uses the values contained in the power_profile.xml file for each device and the BatteryStats and Perfetto services to estimate the energy consumption of each resource / component of the device.

# SETUP

In order to run this tool, the following components are required:
- An Android rooted device (running Android 9 or above);
- A * nix-based environment;
- Android Sdk tools (https://developer.android.com/studio/releases/platform-tools)-

# Installation

## define environment variables

In order to run this tool, there are at least 2 env. variables that need to be defined in the shell startup script (e.g .bashrc or .bash_profile file)

```
export ANDROID_HOME=$HOME/android-sdk/ 
export PATH=$ANDROID_HOME/platform-tools:$PATH
```
## Replicate the enviroment

Install virtual virtualenv enviroment  (via python-pip):
```
$ python -m pip install --user virtualenv
```
##Replicate locally the dev virtualenv

```
$ virtualenv env/
```
## Activate the virtual environment
```
$ source env/bin/activate
```

## Extract power_profile file from device

(In progress)

## Install required packages
```
$ pip install -r requirements.txt
```

# Example
```
# getting the energy consumed in a profiling session (between first and last measurement)
g = GreenStats(power_profile=DEFAULT_PROFILE, timezone="EST")
g.init()
g.start()
do_some_work()
batstats_out_file, perfetto_out_file = g.stop()
g.parseResults( DEFAULT_PROFILE, batstats_out_file , perfetto_out_file )
begin = g.bat_events.events[0].time
end = g.bat_events.events[-1].time
consumption = g.getConsumptionInBetween(begin, end)
print("Energy consumed: %f Joules" % consumption)
```

# TODO
- calibrate the model
- test using flashlight
