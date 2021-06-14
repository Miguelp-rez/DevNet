#!/usr/bin/env python

"""
This script updates interfaces' description according to the source of truth file.
Description format: Connected to {DEVICE} {INTERFACE} – {PURPOSE}.
Goal:
	* Configure interface descriptions on IOS, IOS XE, NX-OS, and IOS XR devices.
	* Save current description on interfaces for audit/change control.
	* Check if devices are actually connected to the interfaces listed in CSV file.
"""
from jinja2 import Template
from collections import defaultdict
from pprint import pprint
import csv

if __name__ == '__main__':
	import argparse
	
	# When a non existing key is accessed, it is initialized with a default value.
	config_commands = defaultdict(dict)

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
				config_commands[row['Device Name']][row['Interface']] = \
					interface_template.render(
						interface_name = row['Interface'],
						connected_device = row['Connected Device'],
						connected_interface = row['Connected Interface'],
						purpose = row['Purpose']
						)

	#print("Config commands generated")
	#pprint(config_commands)
	
	# Display the config commands for the user to review
	for device, interfaces in config_commands.items():
		print(f'Device {device}')
		for interface, configuration in interfaces.items():
			print(configuration)
		print('!\n')


	# Load testbed file
	print(f'Loading {args.testbed}')
	# Connect to all devices
	# Grab current interface descriptions
	# Apply new interface descriptions
	if args.apply:
		print('Applying configurations')
	# Run cdp/lldp commands to grab neighbor information
	# Check if devices are actually connected to the interfaces listed in CSV file.
	# Disconnect from all devices
	# Update source of truth file