# !/bin/bash

# get app pid
# adb shell ps | grep eu.chainfire.supersu | cut -f1 -d\  | sed 's/_//g'

# reset battstas
# adb shell dumpsys batterystats --reset 

# get time in ms 
# date +%s%3N

# extract powe values file
#adb pull  system/framework/framework-res.apk . 
#apktool d -s framework-res.apk -o out/