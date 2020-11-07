import os,re

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

