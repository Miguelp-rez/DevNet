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

# If run as a script
if __name__ == '__main__':
	import argparse

	# Empty dictionary to store the output of the 'show version' command
	# { hostname : {parsed_output} }
	show_version = {}

	# Empty dictionary to store the output of the 'show inventory' command
	# { hostname : {parsed_output} }
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

	# Run commands to gather information from network devices
	for device in testbed.devices.values():
		print(f'Device {device.name}')
		show_version[device.name] = device.parse('show version')
		show_inventory[device.name] = device.parse('show inventory')
		print('show version: ', show_version[device.name])
		print('show_inventory: ', show_inventory[device.name])

	# Disconnect from all devices
	# { hostname : <Device object> }
	for device in testbed.devices.values():
		device.disconnect()
		print(f'Disconnected successfully from {device.name}')

	# Build inventory report

	# Write to a CSV file