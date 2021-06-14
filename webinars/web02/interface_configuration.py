#!/usr/bin/env python

"""
This script updates interfaces' description according to the source of truth file.
Description format: Connected to {DEVICE} {INTERFACE} – {PURPOSE}.
Goal:
	* Configure interface descriptions on IOS, IOS XE, NX-OS, and IOS XR devices.
	* Save current description on interfaces for audit/change control.
	* Check if devices are actually connected to the interfaces listed in CSV file.
"""
from pyats.topology.loader import load
from jinja2 import Template
from collections import defaultdict
from pprint import pprint
import csv

if __name__ == '__main__':
	import argparse
	
	# Interface description commands
	device_config = defaultdict(dict)

	# Output from learn interface model
	interface_details = {}

	# Read command line arguments
	parser = argparse.ArgumentParser(
		description='Updating interface descriptions')
	parser.add_argument(
		'--testbed', required=True, type=str, help='Testbed filename')
	parser.add_argument(
		'--sot', required= True, type=str, help='Source of truth filename')
	parser.add_argument(
		'--apply', action='store_true', help='If set, configurations are applied.')
	
	args = parser.parse_args()

	# Read the source of truth file
	print(f'Reading {args.sot}')
	with open(args.sot, newline='') as csvfile:
		sot = csv.DictReader(csvfile)
		
		# Open configuration template
		with open('config_template.j2') as f:
			interface_template = Template(f.read())
		
		# Loop over each row in the source of truth file
		for row in sot:
			# Remove empty rows
			if row['Device Name']:
				# Create interface descriptions from template
				device_config[row['Device Name']][row['Interface']] = \
					interface_template.render(
						interface_name = row['Interface'],
						connected_device = row['Connected Device'],
						connected_interface = row['Connected Interface'],
						purpose = row['Purpose']
						)

	#print("Config commands generated")
	#pprint(device_config)
	
	# Display the config commands for the user to review
	for device, interfaces in device_config.items():
		print(f'Device {device}')
		for interface, configuration in interfaces.items():
			print(configuration)
		print('!\n')

	# Load testbed file
	print(f'Loading {args.testbed}')
	testbed = load(args.testbed)

	# Connect to all devices
	print(f'Connecting to all devices in {testbed.name}')
	testbed.connect(log_stdout=False)

	# Grab current interface descriptions
	for device in device_config.keys():
		try:
			print(f'Learning current interface configuration for device {device}')
			interface_details[device] = testbed.devices[device].learn('interface')
		except KeyError as e:
			print(f'Error: Device {device} is not in the testbed')

	pprint(interface_details)

	# Apply new interface descriptions
	if args.apply:
		print('Applying configurations')
	# Run cdp/lldp commands to grab neighbor information
	# Check if devices are actually connected to the interfaces listed in CSV file.
	
	# Disconnect from all devices
	
	for device in testbed.devices.values():
		print(f'Disconnecting from {device.name}')
		device.disconnect()

	# Update source of truth file