

# Battery related : https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/os/BatteryManager.java

# https://android.googlesource.com/platform/hardware/interfaces/+/oreo-m5-release/health/1.0/types.hal
BATTERY_STATUS= {
 "unknown" :   1, # "BATTERY_STATUS_UNKNOWN",
 "charging":    2, #  "BATTERY_STATUS_CHARGING",
 "discharging":   3, #; "BATTERY_STATUS_DISCHARGING",
 "not-charging":  4, # "BATTERY_STATUS_NOT_CHARGING",
 "full":  5 # "BATTERY_STATUS_FULL",
}
BATTERY_HEALTH= {
    "unknown":1, # "BATTERY_HEALTH_UNKNOWN",
    "good":2, # "BATTERY_HEALTH_GOOD",
    "overheat":3, # "BATTERY_HEALTH_OVERHEAT",
    "dead":4, # "BATTERY_HEALTH_DEAD",
    "over-voltage":5, # "BATTERY_HEALTH_OVER_VOLTAGE",
    "failure":6, # "BATTERY_HEALTH_UNSPECIFIED_FAILURE",
    "cold":7, # "BATTERY_HEALTH_COLD",
}

BATTERY_PLUGGED= {
    "none": 0 , # : "BATTERY_PLUGGED_NONE"
    "ac": 1 , #  "BATTERY_PLUGGED_AC",
    "usb": 2 , #  "BATTERY_PLUGGED_USB",
    "wireless": 4 , #  "BATTERY_PLUGGED_WIRELESS",
}



# Battery related : https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/os/BatteryManager.java

# https://android.googlesource.com/platform/hardware/interfaces/+/oreo-m5-release/health/1.0/types.hal


#Display
#https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/view/Display.java
DISPLAY_STATE= {
    1: "STATE_OFF",
    2: "STATE_ON",
    3: "STATE_DOZE",
    4: "STATE_DOZE_SUSPEND",
    5: "STATE_DOZE_VR",
    6: "DISPLAY_STATE_ON_SUSPEND"
}

GENERIC_CONSTANTS = {   
        1  :"WAKE_TYPE_FULL" ,
        2  :"WAKE_TYPE_WINDOW" ,
        3  :"SENSOR" ,
        4  :"WIFI_RUNNING" ,
        5  :"FULL_WIFI_LOCK" ,
        6  :"WIFI_SCAN" ,
        7  :"WIFI_MULTICAST_ENABLED" ,
        8  :"VIDEO_TURNED_ON" ,
        9  :"VIBRATOR_ON" ,
        10 :"FOREGROUND_ACTIVITY" ,
        11 :"WIFI_BATCHED_SCAN" ,
        12 :"PROCESS_STATE" ,
        13 :"SYNC" ,
        14 :"JOB" ,
        15 :"AUDIO_TURNED_ON" ,
        16 :"FLASHLIGHT_TURNED_ON" ,
        17 :"CAMERA_TURNED_ON" ,
        18 :"WAKE_TYPE_DRAW" ,
        19 :"BLUETOOTH_SCAN_ON" ,
        20 :"AGGREGATED_WAKE_TYPE_PARTIAL" ,
        21 :"BLUETOOTH_UNOPTIMIZED_SCAN_ON" ,
        22 :"FOREGROUND_SERVICE" ,
        23 :"WIFI_AGGREGATE_MULTICAST_ENABLED" ,
}

STATS={
    0 : "STATS_SINCE_CHARGED",
    1 : "STATS_CURRENT",
    2 : "STATS_SINCE_UNPLUGGED"
}

EVENT_NAMES= {
            "null", 
            "proc", 
            "fg", 
            "top", 
            "sync", 
            "wake_lock_in", 
            "job", 
            "user", 
            "userfg", 
            "conn",
            "active", 
            "pkginst", 
            "pkgunin", 
            "alarm", 
            "stats", 
            "pkginactive", 
            "pkgactive",
            "tmpwhitelist", 
            "screenwake", 
            "wakeupap", 
            "longwake", 
            "est_capacity"
}
