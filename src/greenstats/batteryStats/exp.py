
import datetime,time
import pytz
import shutil
import subprocess

def epochToDate(ts):
	return time.ctime(ts)


def executeShCommand(command):
    pipes = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    std_out, std_err = pipes.communicate()
    output = std_out.decode("utf-8").lower()
    has_error = "error" in output or "not found" in output or "failed" in output

    if pipes.returncode != 0 or has_error:
        err_msg = "%s. Code: %s" % (std_out.decode('utf-8').strip(), pipes.returncode)
        print("error executing command %s" % command)
        print(err_msg)
        return -1    
   
    return output.strip()


matime= executeShCommand("adb shell date  +\'%Y-%m-%d-%H-%M-%S\'")
#matime = "2020-11-13-12-28-30"
print(matime)
tz = "WET"

# naive datetime
d = datetime.datetime.strptime(matime, '%Y-%m-%d-%H-%M-%S')

# add proper timezone
pst = pytz.timezone(tz)
d = pst.localize(d)
#>>> datetime.datetime(2011, 12, 1, 0, 0,
#tzinfo=<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>)

date_timestamp = time.mktime(d.timetuple())
zz = epochToDate(date_timestamp)
print(zz)


# convert to UTC timezone
utc = pytz.UTC
d = d.astimezone(utc)
#>>> datetime.datetime(2011, 12, 1, 8, 0, tzinfo=<UTC>)

# epoch is the beginning of time in the UTC timestamp world
epoch = datetime.datetime(1970,1,1,0,0,0,tzinfo=pytz.UTC)
#>>> datetime.datetime(1970, 1, 1, 0, 0, tzinfo=<UTC>)

# get the total second difference
ts = (d - epoch).total_seconds()
#>>> 1322726400.0