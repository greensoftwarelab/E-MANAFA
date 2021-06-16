TmpWhiteList contains apps that are given temporary network access after receiving a high priority GCM message.

 
 # events:

 - wake_reason: Special case as there are no transitions for this. Just the wake reason that also arrives asynchronously

- wake_lock:  Special case this, as the +w will have the first application to take the wakelocknand -wake_lock may or may not contain the last application to release it.

- screenwake: screen wake reason

- screen: Screen on/off
__
- brigthness: value in [ "dark", "dim", "medium", "light", "bright"]

- wifi - on: wifi_running
	   - active: wifi
	   - scan: wifi_scan

-wakeuppap :  wakeup AP: a UID caused the application processor to wakeup. This can be caused by either +mobile-radio or +wifi, but those don't have to be on the same history line.

- screen - 

-screen_doze - display state: The display is dozing in a low power state; it is still on but is optimized for showing system-provided content while the device is non-interactive. https://developer.android.com/reference/android/view/Display.html#STATE_DOZE
		- equivalent to ambient.on on power profile
		- https://www.protechtraining.com/blog/post/diving-into-android-m-doze-875

- whitelist -  whitelisted from Doze – these apps are not restricted in their alarms, etc.


- bluetooth - even if bluetooth turned off in ui settings, the device keeps scanning if blt is being used for location purposes
- https://github.com/AltBeacon/android-beacon-library/issues/754