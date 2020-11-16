import os,re
import datetime, pytz,time



def convertToUnixTimestamp(batstattime):
	return batstattime	

def convertBatStatTimeToTimeStamp(batstattime):
	secs=[86400,3600,60,1,0.001]
	#secs=[0.001,1,60,3600,86400]
	val=0
	ts = re.split(r'[a-z]+',batstattime)
	ts.reverse()
	for i,x in enumerate(ts):
		if x !="":
			val += secs[(-1)*(i)] * int(x)
	return val


def batStatResetTimeToTimeStamp(matime,timezone):
	d1 =datetime.datetime.strptime(matime, '%Y-%m-%d-%H-%M-%S')
	pst = pytz.timezone(timezone)
	d= pst.localize(d1)
	return time.mktime(d.timetuple())


def convertDateToTimeStamp(date,timezone):
	local = pytz.timezone(timezone)
	time = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
	return "sabonete" + str(time)


def epochToDate(ts):
	return time.ctime(ts)

#x = 1605546434.583252
#print(epochToDate(x))
