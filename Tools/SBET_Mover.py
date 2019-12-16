import glob
import os
import re
import sys
from shutil import copy

def moveFiles():
	if len(os.listdir('05_INS-GPS_PROC/01_POS/')) == 0:
		pass
	else:
		overwrite = input("POS directory not empty. Overwrite? (y/n) ")
		if overwrite == "n":
			return
		elif overwrite == "y":
			sbet = glob.glob("05_INS-GPS_PROC/02_PROJECT/**/**/Proc/sbet_*.out")
		else:
			pass

	sbet = glob.glob("05_INS-GPS_PROC/02_PROJECT/**/**/Proc/sbet_*.out")
	smrmsg = glob.glob("05_INS-GPS_PROC/02_PROJECT/**/**/Proc/smrmsg_*.out")
	piinkaru = glob.glob("05_INS-GPS_PROC/02_PROJECT/**/**/Proc/piinkaru_*.out")
	if sbet:
		copy(sbet[0], "05_INS-GPS_PROC/01_POS/")
		print(sbet[0] + " Moved")
	if smrmsg:
		copy(smrmsg[0], "05_INS-GPS_PROC/01_POS/")
		print(smrmsg[0] + " Moved")
	if piinkaru:
		copy(piinkaru[0], "05_INS-GPS_PROC/01_POS/")
		print(piinkaru[0] + " Moved")

#find rpp files
if len(sys.argv) > 1:
	droppedFile = sys.argv[1]
	os.chdir(droppedFile)

projFilePath = glob.glob('*.rpp')
inProject = 0
if projFilePath:
	inProject = 1
else: 
	projFilePath = glob.glob('**/*.rpp', recursive=True)
	projFilePathNew = []
	for x in projFilePath:
		if "08_RECEIVED" in x:
			pass
			#eliminate duplicate rpp files stored in 08_RECIEVED folder
		else:
			projFilePathNew.append(x)
	projFolderPath = []
	for x in range(0,len(projFilePathNew)):
		projFolderPath.append(os.path.dirname(projFilePathNew[x]))
if inProject == 1:
	moveFiles()
	pass
else:
	origDir = os.getcwd()
	#recursively search and open files
	for i in range(0,len(projFilePathNew)):
		#change working directory to project folder
		os.chdir(projFolderPath[i])
		print("\nRiegl Project: " + projFolderPath[i])
		moveFiles()
		os.chdir(origDir)
input("Press Enter to close")