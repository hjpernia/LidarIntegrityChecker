# LidarIntegrityChecker

>This script verifies multiple components of the project structure from a Riegl LiDAR scanner for quick QA of data in the field and a semi-reliable indication that the data will process successfully.

## Dependencies
* Python
* colorama
	```
	pip install colorama
	```

## Current Features
* Checks in-flight and static T04 files are present for APX-20. Can distinguish.
* IMU remains aligned throughout the flight
* Position remains in DGNSS during flight, reports SPS and DR modes
* RAW file exists for AP-20
* Prints errors and warnings from log
* Checks number of RXP files logged against exists
* Number of EIF files logged against exists
* EIF files are populated for photogrammetry

## Known Compatibility
* Riegl miniVUX-1UAV
* Riegl miniVUX-1UAV-DL

## Known Issues
* If the IMU is initialized before GPS is aquired (rare), the IMU Check function will fail because it cannot grab the GPS time. This will be fixed in the future.
* For AP-20 IMUs, does not check if the RAW file is complete, only that it exists. Will check size against run time in the future.