import glob
import os
import re
from colorama import init
init()
from colorama import Fore, Back, Style
from datetime import datetime
from datetime import timedelta

#regex
dateSearch = re.compile(r'[12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])')
timeSearch = re.compile(r'[012]\d:\d{2}:\d{2}\.\d{3}')
dateTimeSearch = re.compile(r'(([12]\d{3})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\ ([012]\d):(\d{2}):(\d{2})\.(\d{3}))')

#vars
alignCheck = 0
alignTime = []
DTF = '%Y-%m-%d %H:%M:%S.%f'
takeoff = 0
logNum = 0

#open rpl file
logFilePath = glob.glob('*.rpl')
openLog = open(logFilePath[0], "r")

#forward search
for line in openLog: 	
	startDate = dateTimeSearch.search(line).group()
	if startDate:
		break

openLog.seek(0)

for line in openLog:
	#look for takeoff
	if "System movement detected" in line:
		#grab timestamp on line
		startIMU = dateTimeSearch.search(line).group()
		takeoff = 1
			##for line in openLog:
		#check IMU stays aligned during records after takeoff
	if "Aligned" in line:
		alignCheck = 1
		alignTime = dateTimeSearch.findall(line)
		##print(alignCheck)
		if len(alignTime) <= 1:
			print(Fore.RED, "Aligned without GPS Sync. I can't handle this yet!", Style.RESET_ALL)
	if "Degraded" in line:
		alignCheck = 0
	if "Working-Logging" in line and alignCheck != 1 and takeoff == 1:
		logNum += 1
		print(Fore.YELLOW, "Warning! IMU degraded during part of flight!", Style.RESET_ALL)
		
##print(alignTime)
alignTimeScanner = datetime.strptime(alignTime[0][0],DTF)
alignTimeGPS = datetime.strptime(alignTime[1][0],DTF)
timeOffset = alignTimeGPS-alignTimeScanner
##print(timeOffset)
		
openLog.seek(0)

#reverse search for end of last record
for line in reversed(list(openLog)):
	#looking for last instance of switch to working
	if "Stop Logging" in line:
		#grab time and date on line
		endIMU = dateTimeSearch.search(line).group()
		break

#t04 date/time formatting conversion
startIMU = datetime.strptime(startIMU,DTF)
endIMU = datetime.strptime(endIMU,DTF)
startIMU = startIMU + timeOffset 
endIMU = endIMU + timeOffset
startIMU = startIMU.replace(second=0, microsecond=0)
endIMU = endIMU.replace(second=0, microsecond=0)
##print(startIMU)
##startT04Crit = re.sub(':|\.','',startIMU)
##endT04Crit = re.sub(':|\.','',endIMU)

#flight time delta
staticTime = int(input("Input Static Time in Minutes: "))
startIMU -= timedelta(minutes=staticTime)
endIMU += timedelta(minutes=staticTime)

startT04File = startIMU.strftime("%y%m%d%H%M")
endT04File = endIMU.strftime("%y%m%d%H%M")
t04Delta = endIMU - startIMU

t04Files = glob.glob("02_INS-GPS_Raw/02_FULL/*/*")
t04Count = 0

for i in range(int(t04Delta.seconds/60)):
	t04Check = 0
	currFile = startIMU
	currFile+=timedelta(minutes=i)
	t04Name = currFile.strftime("%y%m%d%H%M")
	for x in t04Files:
		if t04Name in x:
			t04Count += 1
			t04Check = 1
	if t04Check == 0: 
		if i < staticTime or i > int(t04Delta.seconds/60)-staticTime:
			print(Fore.YELLOW, "Static " + t04Name + ".T04 Missing!", Style.RESET_ALL)
		else: print(Fore.RED, "In Flight " + t04Name + ".T04 Missing!", Style.RESET_ALL)

print(Fore.GREEN, "\n " + str(t04Count) + " T04 Files Found", Style.RESET_ALL)



#print(startDate)
#print(endIMU)
#print(endDate)
openLog.close()

########New program. FIX THIS############

#open rpl file
logfile = glob.glob('*.rpl')
searchlog = open(logfile[0], "r")
errorcount = 0
warncount = 0

#Search rpl file for errors/warnings

for line in searchlog:
	if "<!>" in line: 
		warncount+=1
	if "[x]" in line: 
		errorcount+=1
		##print(Fore.RED, Back.BLACK, line, Style.RESET_ALL)
		
print(Fore.RED, str(errorcount)+' Log Errors Found', Style.RESET_ALL)
print(Fore.YELLOW, str(warncount)+' Log Warnings Found', Style.RESET_ALL)

#account for all rxp files
searchlog.seek(0)
rxpCount=0
rxpFiles=[]
rxpPathStart=0
rxpPathEnd=0
for line in searchlog:
	if ".rxp" in line:
		rxpCount+=1
		rxpPathStart=line.find("/03")
		rxpPathEnd=line.find("'<")
		rxpFiles.append(line[rxpPathStart:rxpPathEnd])

print(Fore.GREEN, str(rxpCount)+" RXP Files Generated\n", Style.RESET_ALL)
rxpFound=0
for rxpName in rxpFiles:
	exists = os.path.isfile("."+rxpName)
	if exists: 
		rxpFound+=1
	else: 
		print(Fore.RED, Back.BLACK,"RXP '"+rxpName+"' Missing!", Style.RESET_ALL)
		
if rxpCount == rxpFound: print(Fore.GREEN, "All "+str(rxpFound)+" RXP Files Found!", Style.RESET_ALL)
else: print(Fore.RED, "Error, check for missing RXP files!", Style.RESET_ALL)

searchlog.close()