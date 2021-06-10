#!/usr/bin/env python

"""
This script create a network inventory file with CSV format.

Goals
	* Connect to all devices in the network.
	* Run the show_version and show_inventory commands in each device.
	* Generate a CSV file with the following information:
		- device name,
		- software version,
		- uptime,
		- serial number.

Usage
	./network_inventory <./path/to/testbed_file>
"""

from pyats.topology.loader import load
from genie.metaparser.util.exceptions import SchemaEmptyParserError
from genie.libs.parser.utils.common import ParserNotFound
from pprint import pprint

"""
This fuction tries to parse a command on a device, but
returns raw output in case the command is not supported
"""
def parse_command(device, command):
	print(f'Running {command} on {device.name}')
	try:
		output = device.parse(command)
		return {'type': 'parsed', 'output': output}
	except SchemaEmptyParserError:
		print(f'Parsed {command}, but it returned empty')
	except ParserNotFound:
		print(f'Parser for {command} is not supported in {device}')

	# Execute the command anyway, but return raw output
	output = device.execute(command)
	return {'type': 'raw', 'output': output}

"""
This function process device-specific information and 
returns standardized output
	IOS XR
	# software version: show_version[hostname][output][software_version]
	#	'6.3.1'
	# uptime: show_version[hostname][output][uptime]
	#	'1 hour, 59 minutes'
	# serial number: show_inventory is missing
	#
	IOS XE
	# software version: show_version[hostname][output][version][version]
	#	'16.11.1b'
	# uptime: show_version[hostname][output][version][uptime]
	#	'1 hour, 58 minutes'
	# serial number: show_inventory[hostname][output][chassis][MODEL][sn]]
	#	'910GSDMVQ2T'
	# MODEL = show_version[hostname][output][version][chassis]
	#	'CSR1000V'
	#
	NX-OS
	# software version: show_version[output][platform][software][system_version]
	#	'9.2(3)'	
	# uptime: show_version[output][platform][kernel_uptime] 
	# 	{'days': 0, 'hours': 0, 'minutes': 24, 'seconds': 29}
	# serial number: show_inventory[hostname[output][name][Chassis][serial_number]
	#	'9RDIN8H58L9'
	#
	ASA
	# software version: show_version[hostname][output]
	# 	Cisco Adaptive Security Appliance Software Version 9.12(2)
	# uptime: show_version[hostname][output]
	# 	edge-firewall01 up 1 hour 20 mins
	# serial number: show_inventory[hostname][output][Chassis][sn]
	#	'9ABC7VGUPFA'
	#
	IOSV
	# software_version: show_version[hostname][output][version][version]
	#	'15.2(CML'
	# uptime: show_version[hostname][output][version][uptime]
	#	'1 hour, 59 minutes'
	# serial number: show_inventory is missing
	# show_version[hostname][output][version][chassis_sn]
	#	'99GVDCAYZ1T'
"""
def get_inventory(device, show_version, show_inventory):
	# Common information for all devices
	hostname = device.name
	device_os = device.os

	if device_os == 'iosxr':
		software_version = None
		uptime = None
		serial_number = None
	elif device_os == 'iosxe':
		software_version = None
		uptime = None
		serial_number = None
	elif device_os == 'nxos':
		software_version = None
		uptime = None
		serial_number = None
	elif device_os == 'asa':
		software_version = None
		uptime = None
		serial_number = None
	elif device_os == 'iosxr':
		software_version = None
		uptime = None
		serial_number = None
	else:
		return False

	return (hostname, device_os, software_version, uptime, serial_number)

# If run as a script
if __name__ == '__main__':
	import argparse

	# Empty dictionary to store the output of the 'show version' command
	# { hostname : {type : output} }
	show_version = {}

	# Empty dictionary to store the output of the 'show inventory' command
	# { hostname : {type : output} }
	show_inventory = {}

	# Read testbed filename
	parser = argparse.ArgumentParser(description='testing pyATS')
	parser.add_argument('testbed', type=str, help='pyATS testbed filename')
	args = parser.parse_args()

	# Load testbed file
	print(f'Loading {args.testbed} file')
	testbed = load(args.testbed)

	# Connect to all devices, but silent logs
	print(f'Connecting to all devices in {testbed.name}')
	testbed.connect(log_stdout=False)

	# testbed.devices = { hostname : <Device object> }
	for device in testbed.devices.values():
		# Run commands to gather information from network device
		show_version[device.name] = parse_command(device,'show version')
		# pprint(show_version[device.name])

		show_inventory[device.name] = parse_command(device, 'show inventory')
		# pprint(show_inventory[device.name])

		# Build network inventory
		get_inventory(device, show_inventory, show_version)
		
		# Disconnect from device
		device.disconnect()
		print(f'Disconnected successfully from {device.name}')


	
	# Write to a CSV file