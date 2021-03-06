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
from datetime import datetime
from time import sleep
import csv

if __name__ == '__main__':
	import argparse
	
	# Interface description commands
	devices_config = defaultdict(dict)

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
	parser.add_argument(
		'--check', action='store_true', help='If set, compare lldp neighbors against the SoT file')
	
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
				# Create interface descriptions commands from the template
				devices_config[row['Device Name']][row['Interface']] = \
					interface_template.render(
						interface_name = row['Interface'],
						connected_device = row['Connected Device'],
						connected_interface = row['Connected Interface'],
						purpose = row['Purpose']
						)

	# Debuggin information
	#print("Config commands generated")
	#pprint(devices_config)
	
	# Load testbed file
	print(f'Loading {args.testbed}')
	testbed = load(args.testbed)

	# Connect to all devices
	print(f'Connecting to all devices in {testbed.name}')
	testbed.connect(log_stdout=False)

	# Grab current interface descriptions for devices in the SoT file
	for device in devices_config.keys():
		try:
			print(f'Learning current interface configuration for device {device}')
			interface_details[device] = testbed.devices[device].learn('interface')
		except KeyError as e:
			print(f'Error: Device {device} is not in the testbed')

	# Debugging information
	# Display current interface descriptions
	# {device : <interface_object> }
	#for device, interfaces in interface_details.items():
	#	print(f'Current configuration for device {device}')
	#	for interface, details in interfaces.info.items():
	#		try:
	#			print(f'Interface {interface} {details["description"]}')
	#		except KeyError:
	#			print(f'Interface {interface} does not have a description')
	#	print('!\n')

	# Display the config commands for the user to review
	# {device : {interface01 : 'config_commands', interface02 : config_commands ...}}
	for device, interfaces in devices_config.items():
		print(f'\nNew configurations for device {device}')
		for interface, configuration in interfaces.items():
			print(configuration)
		print('!\n')

		# Apply new interface descriptions
		if args.apply:
			# Confirm if the user truly wants to apply the configuration
			confirm = input(f'Do you want to apply configuration to {device}? (y/n) ')
			if confirm == 'y':
				if device in testbed.devices:
					print(f'Applying configurations to {device}')
					# Many errors can ocurr when sending commands
					try:
						# Send all config commands at once
						output = testbed.devices[device].configure(
							'\n'.join(interfaces.values())
							)
						# Debugging information
						# print(output)
					except Exception as e:
						print(f'Error: Configuration to {device} failed')
						print(e)
				else:
					print(f'Error: Device {device} is not in the testbed')
		print('\n--------------------------------------')

	if args.check:
		print('Checking lldp neighbors against the SoT file')
		# Output from the show lldp neighbors detail parser
		lldp_info = {}

		# Enable lldp
		# Only work with devices in the SoT file
		
		for device in devices_config:
			if device in testbed.devices:
				print(f'Enabling lldp on device {device}')
				# Many errors can occurr while sending commands
				try:
					testbed.devices[device].api.configure_lldp()
				except Exception as e:
					print(f'Error: Failed to enable lldp on {device}')
					# Debugging information
					print(e)
			else:
				print(f'Error: Device {device} is not in the testbed')

		# Wait for neighbor relationships to form
		print('\nWaiting for neighbor relationships to form...\n')
		sleep(30)
		
		for device in devices_config:
			if device in testbed.devices:
				print(f'Learning lldp neighbors of device {device}')
				
				# Run cdp/lldp commands to grab neighbor information
				try:
					lldp_info[device] = testbed.devices[device].parse(
						'show lldp neighbors detail')					
				except Exception as e:
					print(f'Error: Failed to run lldp commands on {device}')
					# Debugging information
					print(e)
			else:
				print(f'Error: Device {device} is not in the testbed')
		
		# Debuggin information
		# pprint(lldp_info)
		# device :
		# {
		#	'interfaces' : 
		#	{
		#		interfaceX : 
		#		{
		#			'port-id' : 
		#			{
		#				portX : 
		#				{
		#					'neighbors' : 
		#					{
		#						hostnameX : {more_stuff}
		#					}
		#				}
		#			}
		#		}
		#	}
		# {

		# Check if devices are actually connected to the interfaces listed in CSV file.
		# 	Correct - lldp neighbors match the sot file
		# 	Incorrect - lldp neighbors differ from the sot file
		# 	Unknown - lldp information is not available

		test_results = defaultdict(dict)
		with open(args.sot, newline='') as sot_file:
			sot = csv.DictReader(sot_file)
			for row in sot:
				device = row['Device Name']
				# Ignore blank rows and devices with no lldp entry
				if device:
					# Ignore devices without an lldp entry
					if device in lldp_info.keys():
						interface = row['Interface']
						# Ignore interfaces that does not have neighbor relationships
						if interface in lldp_info[device]['interfaces'].keys():
							connected_device = row['Connected Device']
							connected_interface = row['Connected Interface']
							# Check if port_id matches information in the SoT
							neighbor_interface = lldp_info[device]['interfaces'][interface]['port_id'].keys()
							if connected_interface in neighbor_interface:
								# Check if neighbor hostname matches information in the SoT
								neighbor_hostname = lldp_info[device]['interfaces'][interface]['port_id'][connected_interface]['neighbors'].keys()
								if  connected_device in neighbor_hostname:
									test_results[device][interface] = 'Correct'
								else:
									# In some cases lldp neighbor_name differs from the SoT because
									# neighbor_name = core-rtr01.virl.info 
									# connected_device = core-rtr01
									test_results[device][interface] = 'Incorrect - connected to ' + (list(neighbor_hostname)[0])
							else:
								test_results[device][interface] = 'Incorrect - connected to ' + (list(neighbor_interface)[0])
						else:
							print(f'WARNING: Device {device} {interface} does not have any neighbor relationships')
							test_results[device][interface] = 'Unknown - No LLDP neighbor info'
					else:
						print(f'WARNING: LLDP is not enabled for device {device}')
						test_results[device][row['Interface']] = 'Unknown - LLDP is not enabled'

		# Debugging information
		# pprint(test_results)

	# Disconnect from all devices
	for device in testbed.devices.values():
		print(f'Disconnecting from {device.name}')
		device.disconnect()

	# Update source of truth file
	with open(args.sot, newline='') as sot_file:
		sot = csv.DictReader(sot_file)

		now = datetime.now()
		report_filename = f'{now.strftime("%Y-%m-%d-%H-%M-%S")}_interface_config_report.csv'

		# Create a list of field headers for the report
		report_headers = sot.fieldnames + ['Old Description']

		# Add a new header for lldp neighbor test results
		if args.check:
			report_headers.append('LLDP neighbor test')

		# Open report file
		print(f'Writing report to {report_filename}')

		with open(report_filename, 'w', newline='') as report_file:
			writer = csv.DictWriter(report_file, fieldnames=report_headers)

			writer.writeheader()

			# Read a line from SoT file
			for line in sot:
				try:
					line['Old Description'] = \
						interface_details[line['Device Name']].info[line['Interface']]['description']
				except KeyError:
					# Interface does not have a description
					line['Old Description'] = ''

				try:
					line['LLDP neighbor test'] = \
						test_results[line['Device Name']][line['Interface']]
				except KeyError as e:
					# Empty line
					line['LLDP neighbor test'] = ''

				# Write that line, plus the new fields
				writer.writerow(line)
