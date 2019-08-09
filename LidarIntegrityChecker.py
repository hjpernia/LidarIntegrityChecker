import glob
import os
import re
import csv
from colorama import init, Fore, Back, Style
from datetime import datetime, timedelta
init()

#find rpl files
logFilePath = glob.glob('*.rpl')
inProject = 0
if logFilePath:
	inProject = 1
else: 
	logFilePath = glob.glob('**/*.rpl', recursive=True)
	for x in logFilePath:
		if "08_RECEIVED" in x:
			#eliminate duplicate rpl files stored in 08_RECIEVED folder
			logFilePath.remove(x)
	logFolderPath = []
	for x in range(0,len(logFilePath)):
		logFolderPath.append(os.path.dirname(logFilePath[x]))

def fIMUCheck():
	#vars
	alignCheck = 0
	alignTime = []
	DTF = '%Y-%m-%d %H:%M:%S.%f'
	takeoff = 0
	logNum = 0
	startIMU = -1
	#regex
	dateSearch = re.compile(r'[12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])')
	timeSearch = re.compile(r'[012]\d:\d{2}:\d{2}\.\d{3}')
	dateTimeSearch = re.compile(r'(([12]\d{3})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\ ([012]\d):(\d{2}):(\d{2})\.(\d{3}))')

	openLog.seek(0)

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
		##check IMU stays aligned during records after takeoff
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
	if startIMU == -1:
		print(Fore.YELLOW, "AP20 IMU or No Takeoff Detected. Press Enter:", Style.RESET_ALL)
		input("")
		rawFile = glob.glob("02_INS-GPS_Raw/02_FULL/*/*.raw")
		if rawFile:
			print(Fore.GREEN, "IMU RAW File Found!", Style.RESET_ALL)
		else:
			print(Fore.RED, "No IMU RAW File Found!", Style.RESET_ALL)
		return
	openLog.seek(0)
	#reverse search for end of last record
	for line in reversed(list(openLog)):
		#looking for last instance of switch to working
		if "Stop Logging" in line:
			#grab time and date on line
			endIMU = dateTimeSearch.search(line).group()
			break

	openLog.seek(0)
	##get time offset
	alignTimeScanner = datetime.strptime(alignTime[0][0],DTF)
	alignTimeGPS = datetime.strptime(alignTime[1][0],DTF)
	timeOffset = alignTimeGPS-alignTimeScanner

	#t04 date/time formatting conversion
	startIMU = datetime.strptime(startIMU,DTF)
	endIMU = datetime.strptime(endIMU,DTF)
	startIMU = startIMU + timeOffset
	endIMU = endIMU + timeOffset
	startIMU = startIMU.replace(second=0, microsecond=0)
	endIMU = endIMU.replace(second=0, microsecond=0)

	#flight time delta
	staticTime = int(input("Input Static Time in Minutes: "))
	startIMU -= timedelta(minutes=staticTime)
	endIMU += timedelta(minutes=staticTime)

	startT04File = startIMU.strftime("%y%m%d%H%M")
	endT04File = endIMU.strftime("%y%m%d%H%M")
	t04Delta = endIMU - startIMU

	t04Files = glob.glob("02_INS-GPS_Raw/02_FULL/*/*")
	t04Count = 0

	#loop through time delta for filenames
	for i in range(int(t04Delta.seconds/60)):
		t04Check = 0
		currFile = startIMU
		currFile+=timedelta(minutes=i)
		t04Name = currFile.strftime("%y%m%d%H%M")
		#check filenames present in list
		for x in t04Files:
			if t04Name in x:
				t04Count += 1
				t04Check = 1
		#print error if file missing
		if t04Check == 0:
			if i < staticTime or i > int(t04Delta.seconds/60)-staticTime:
				print(Fore.YELLOW, "Static " + t04Name + ".T04 Missing!", Style.RESET_ALL)
			else: print(Fore.RED, "In Flight " + t04Name + ".T04 Missing!", Style.RESET_ALL)

	#total discovered t04s
	print(Fore.GREEN, "\n " + str(t04Count) + " T04 Files Found", Style.RESET_ALL)

	openLog.seek(0)
	
	#additionl vars
	errorcount = 0
	warncount = 0

	#Search rpl file for errors/warnings
	for line in openLog:
		if "<!>" in line:
			warncount+=1
		if "[x]" in line:
			errorcount+=1
			##print(Fore.RED, Back.BLACK, line, Style.RESET_ALL)
	if errorcount > 2:
		print(Fore.RED, str(errorcount)+' Log Errors Found', Style.RESET_ALL)
	if warncount > 2:
		print(Fore.YELLOW, str(warncount)+' Log Warnings Found', Style.RESET_ALL)

def fRXPCheck():
	##check reported rxp files are present in file structure##
	openLog.seek(0)
	rxpName = []
	rxpSearch = re.compile(r'\d{6}_\d{6}_.{0,}.rxp')
	rxpFound = 0
	#search log for reported rxp files
	for line in openLog:
		if rxpSearch.search(line):
			rxpName.append(rxpSearch.search(line)[0])
	rxpFiles = glob.glob("03_RIEGL_RAW/02_RXP/**/*.rxp")
	rxpCount = len(rxpName)
	#compare reported rxp and existing rxps
	for i in rxpName:
		rxpCheck = 0
		for x in rxpFiles:
			if i in x:
				rxpCheck = 1
				break
		if rxpCheck == 1:
			rxpFound += 1
		else:
			print(Fore.RED, Back.BLACK,"RXP " + i +" Missing!", Style.RESET_ALL)
	if rxpFound == rxpCount: print(Fore.GREEN, "All "+str(rxpFound)+" RXP Files Found!", Style.RESET_ALL)
	else: print(Fore.RED, "Error, check for missing RXP files!", Style.RESET_ALL)

def fCamCheck():
	##check reported eif files are present in file structure##
	openLog.seek(0)
	eifName = []
	eifSearch = re.compile(r'\d{6}_\d{6}.eif')
	eifFound = 0
	#search log for reported eif files
	for line in openLog:
		if eifSearch.search(line):
			eifName.append(eifSearch.search(line)[0])
	#grab filenames of all existing eif files
	eifFiles = glob.glob("04_CAM_RAW/01_EIF/**/*.eif")
	eifCount = len(eifName)
	#compare reported eif and existing eifs
	for i in eifName:
		eifCheck = 0
		for x in eifFiles:
			if i in x:
				eifCheck = 1
				break
		if eifCheck == 1:
			eifFound += 1
		else:
			print(Fore.RED, Back.BLACK,"EIF " + i +" Missing!", Style.RESET_ALL)
	if eifFound == eifCount and eifCount > 0: print(Fore.GREEN, "All "+str(eifFound)+" EIF Files Found!", Style.RESET_ALL)
	elif eifFound != eifCount: print(Fore.RED, "Error, check for missing EIF files!", Style.RESET_ALL)
	else: print(Fore.YELLOW, "No EIF files found. Camera present?", Style.RESET_ALL)

	##now check contents of eif file##
	eifPop = 1
	#loop through all eif files in project
	for x in eifFiles:
		rowCount = 0
		#open eif file
		with open(x,  mode = 'r', newline = '') as eifOpen:
			#escapechar used to solve problem with souble quotes present in file
			eifRead = csv.reader(eifOpen, escapechar = '"', delimiter = ';')
			rpyCheck, opkCheck, geoCheck = 1,1,1
			#loop through eif row by row
			for row in eifRead:
				rowCount += 1
				#skip first two header rows
				if rowCount > 3:
					#check all relevant columns are not empty and do not contain zeros
					if not row[3] or not row[4] or not row[5]:
						rpyCheck = 0
					elif row[3] == '0' or row[4] == '0' or row[5] == '0':
						rpyCheck = 0
					if not row[6] or not row[7] or not row[8]:
						opkCheck = 0
					elif row[6] == '0' or row[7] == '0' or row[8] == '0':
						opkCheck = 0
					if not row[9] or not row[10] or not row[11]:
						geoCheck=0
					elif row[9] == '0' or row[10] == '0' or row[11] == '0':
						geoCheck = 0
			#if check toggled false print error
			if rpyCheck == 0:
				print(Fore.RED, Back.BLACK,"\nRoll/Pitch/Yaw Values missing in " + x, Style.RESET_ALL)
				eifPop = 0
			if opkCheck == 0:
				print(Fore.RED, Back.BLACK,"\nOmega/Phi/Kappa Values missing in " + x, Style.RESET_ALL)
				eifPop = 0
			if geoCheck == 0:
				print(Fore.RED, Back.BLACK,"\nLat/Lon/Alt Values missing in " + x, Style.RESET_ALL)
				eifPop = 0
		eifOpen.close()
	#check no eif data missing and eif files actually exist
	if eifPop == 1 and eifFound > 0:
		print(Fore.GREEN, "All EIF Files Populated!", Style.RESET_ALL)

if inProject == 1:
	openLog = open(logFilePath[0], "r")
	fIMUCheck()
	fRXPCheck()
	fCamCheck()
	openLog.close()	
else:
	origDir = os.getcwd()
	#recursively search and open files
	for i in range(0,len(logFilePath)):
		openLog = open(logFilePath[i], "r")
		#change working directory to project folder
		os.chdir(logFolderPath[i])
		print("\nRiegl Project: " + logFolderPath[i])
		fIMUCheck()
		fRXPCheck()
		fCamCheck()
		openLog.close()
		#return to original parent directory
		os.chdir(origDir)
input("Press Enter to close")