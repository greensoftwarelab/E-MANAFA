# E-MANAFA: Energy Monitor and ANAlyzer For Android

E-MANAFA is a software model-based tool for performing fine-grained estimates of energy consumption on Android devices. For this purpose, it uses values from power_profile.xml and from the BatteryStats and Perfetto services to estimate the energy consumption of each resource / component of the device. 


# SETUP

In order to run this tool, the following resources are required:
- A rooted Android device (running Android 9 or above);
- A *nix-based environment (MAC OS , Linux);
- Python 3.6 or above;
- Android Sdk tools (https://developer.android.com/studio/releases/platform-tools)

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

## Extract power_profile.xml file from device
Note: 
```



# Install required packages
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

# Supported devices:
This tool can be used with any Android device able to run the Perfetto, that is available since Android 9 (P). The tool so far was successfuly executed on the following devices:
- Pixel 3a
- Pixel 4a 5G
- Xiaomi Mi 9 Lite

# TODO
- calibrate the model
- test using flashlight
- Retrieve consumption per component 
