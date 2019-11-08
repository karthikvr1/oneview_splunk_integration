#
###
# (C) Copyright (2019) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###


import logging
import json
import os
from time import sleep
import subprocess
import sys
import re
import requests
import base64
import signal
from datetime import datetime


##################################################################
# Validate OneView appliance details.
# Function needs to be added with new parameters when updated in Json
##################################################################
def validate_oneview_details(oneViewDetails):
	
	required_fields = ('host','alias','user','authLoginDomain', 'passwd','action','route','alert_type')
	# Validate inputs
	if not all(keys in oneViewDetails for keys in required_fields):
		logging.error("Oneview details incomplete.")
		logging.error(
			"Please ensure following values present in input json file:- host, user, passwd, action, route")
		sys.exit(1)
		
	# Decode password
	# password = base64.b64decode(oneViewDetails['passwd'].encode('utf-8')) 
	# oneViewDetails['passwd'] = password.decode('utf-8')


##################################################################
# Init the logging module.
##################################################################
def initialize_logging(oneViewIP, loggingLevel='WARNING'):
	# Initialize the log file path, log format and log level
	logfiledir = os.getcwd() + os.sep + "logs"
	if not os.path.isdir(logfiledir):
		os.makedirs(logfiledir)

	logfile = logfiledir + os.sep +"OneViewNagios_{}.log".format(oneViewIP)
	if os.path.exists(logfile):
		fStats = os.stat(logfile) 
		if fStats.st_size >= 1024000:
			#Backing up logfile if size is more than 1MB
			timestamp = '{:%Y-%m-%d_%H_%M}'.format(datetime.now())
			#Backup logfile
			os.rename(logfile,logfiledir + os.sep + 'OneViewNagios_{}_'.format(oneViewIP)+ timestamp +".log")
			#Create empty logfile
			open(logfile, 'a').close()
	else:
		#Create empty logfile
		open(logfile, 'a').close()

	# Init the logging module with default log level to INFO. 
	logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%d-%m-%Y:%H:%M:%S', level=loggingLevel)


##################################################################
# Validate hardware types give in input file
# Function needs to be added with new parameters when updated in Json
##################################################################
def validate_hardware_category(oneViewDetails,hardwareTypes):

	# Get hardware category as list
	hardwareType = oneViewDetails["alert_hardware_category"]
	alertHardwareTypes = hardwareType.split(':')
	# config['alertHardwareTypes'] = alertHardwareType

	for hardware in alertHardwareTypes:		
		if not hardware in hardwareTypes:
			logging.error("Hardware type - \"{}\" is not permissible. Valid types - {} \nExiting.. ".format(hardware,hardwareTypes))
			print("Hardware type - \"{}\" is not permissible. Valid types - {} \nExiting.. ".format(hardware,hardwareTypes))
			sys.exit(1)
		elif not hardware:
			logging.error("Enter interested hardware types in config file. Exiting...")
			sys.exit(1)

##################################################################
# Validate Validate alert types give in input file
# Function needs to be added with new parameters when updated in Json
##################################################################
def validate_alert_types(oneViewDetails, alertTypes):
	## Validating the alert type to be sent to Nagios
	#
	inputAlertTypes = oneViewDetails["alert_type"].split(':')
	inputAlertTypes = [x.lower() for x in inputAlertTypes] # User interested alert types
	# config['inputAlertTypes'] = inputAlertTypes

	alertTypes = [a.lower() for a in alertTypes] # List of permissible alerts
	
	## All of the alert types entered by user should match with actual alert types.
	## If there is any mismatch, the same is printed in the log file and program will exit. 
	for alertType in inputAlertTypes:		
		if not alertType in alertTypes:
			logging.error("Alert type mismatch : " + alertType + ". Kindly review and restart the plugin.")
			sys.exit(1)
		elif not alertType:
			logging.error("Enter interested alert types in config file. Exiting...")
			sys.exit(1)


