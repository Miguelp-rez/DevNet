#!/usr/bin/env python

"""
This script updates interfaces' description according to the source of truth file.
Description format: Connected to {DEVICE} {INTERFACE} – {PURPOSE}.
Goal:
	* Configure interface descriptions on IOS, IOS XE, NX-OS, and IOS XR devices.
	* Save current description on interfaces for audit/change control.
	* Check if devices are actually connected to the interfaces listed in CSV file.
"""

if __name__ == '__main__':
	import argparse
	
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

	# Create interface descriptions

	# Load testbed file
	print(f'Loading {args.testbed}')
	if args.apply:
		print('Applying configurations')
	
	# Connect to all devices
	# Grab current interface descriptions
	# Apply new interface descriptions
	# Run cdp/lldp commands to grab neighbor information
	# Check if devices are actually connected to the interfaces listed in CSV file.
	# Disconnect from all devices
	# Update source of truth file