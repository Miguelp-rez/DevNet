#!/usr/bin/env python

"""
This is test script to explore the pyATS library

Goal:
	* Connect to one device and parse the output of the 'show version' command
"""

from pyats.topology.loader import load

# If run as a script
if __name__ == '__main__':
	import argparse

	# Empty dictionary to store the output of the 'show version' command.
	# { hostname : {parsed_output} }
	show_version = {}

	# Read testbed filename
	parser = argparse.ArgumentParser(description='testing pyATS')
	parser.add_argument('testbed', type=str, help='pyATS testbed filename')
	args = parser.parse_args()

	# Load testbed file
	testbed = load(args.testbed)

	# Grab one device
	device = testbed.devices['dist-rtr01']

	# Show testbed device methods
	# print(dir(device))

	# Connect to device, but silent logs
	device.connect(log_stdout = False)
	if device.is_connected():
		print(f'Successful connection to {device.name}')
		# The execute method returns a string with raw output
		# show_version[device.name] = device.execute('show version')
		
		# The parse method returns a dictionary with nicely formatted data
		show_version[device.name] = device.parse('show version')

		# Show the result
		print(show_version[device.name])

	device.disconnect()
	if device.is_connected():
		print('Error disconnecting')
	else:
		print(f'Disconnected successfully from {device.name}')