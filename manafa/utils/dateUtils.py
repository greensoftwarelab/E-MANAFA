import os,re
import datetime, pytz,time



def convertToUnixTimestamp(batstattime):
	return batstattime	

def convertBatStatTimeToTimeStamp(batstattime,timezone="EST"):
	#secs=[86400,3600,60,1,0.001]
	secs = [0.001, 1, 60, 3600, 86400]
	val = 0.0
	ts = re.split(r'[a-z]+', batstattime.strip())
	ts.reverse()
	ts = filter(lambda x: x != '', ts)
	for i, x in enumerate(ts):
		#print(x)
		val += float(x) * secs[i]
		#print(val)
	return val
	#d1 =datetime.datetime.strptime(batstattime, '%Y-%m-%d-%H-%M-%S')
	#pst = pytz.timezone(timezone)
	#d= pst.localize(d1)
	#return time.mktime(d.timetuple())

def batStatResetTimeToTimeStamp(matime, timezone="UTC"):
	d1 =datetime.datetime.strptime(matime, '%Y-%m-%d-%H-%M-%S')
	pst = pytz.timezone(timezone)
	d= pst.localize(d1)
	return time.mktime(d.timetuple())


def convertDateToTimeStamp(date,timezone="EST"):
	local = pytz.timezone(timezone)
	#time = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
	return time
	#return None

def epochToDate(ts):
	return time.ctime(ts)

#x="2020-11-17-12-06-18"
#z = batStatResetTimeToTimeStamp(x)
#print(z)
#t2 = "1s394ms"
#t2 = "3d23h23m38s126ms"
#zz = convertBatStatTimeToTimeStamp(t2)
#print(zz)
#z = z+zz
#print(z)


