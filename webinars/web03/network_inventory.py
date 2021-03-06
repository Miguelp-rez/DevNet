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
	./network_inventory </path/to/testbed_file>
"""

from pyats.topology.loader import load
from genie.metaparser.util.exceptions import SchemaEmptyParserError
from genie.libs.parser.utils.common import ParserNotFound
from datetime import datetime
from getpass import getpass
from urllib3 import disable_warnings, exceptions
import requests
import csv

"""
Plan for SDN inventory
1 Add command line arguments for details of the ACI and SD-WAN controllers.
2 Ask the user for credentials (if needed)
3 Authenticate to the APIs
4 Make HTTP GET requests to gather data from the APIs.
5 Update report 
"""


"""
This function authenticates to the ACI REST API.
If an error ocurrs, it returns False.
"""
def auth_aci(aci_address, aci_username, aci_password):
	# Build URL
	url = f'https://{aci_address}/api/aaaLogin.json'
	# Build credentials dictionary
	body = {
			    "aaaUser": {
			        "attributes" : {
			            "name" : aci_username,
			            "pwd" : aci_password
			        }
			    }
			}

	# Make request
	try:
		reponse = requests.post(url, json=body, verify=False)
		# Return token
		if reponse.status_code == 200:
			return reponse.json()['imdata'][0]['aaaLogin']['attributes']['token']
		else:
			print('Bad request. Maybe wrong credentials.')
	except Exception as e:
		print('Unable to authenticate to the ACI REST API')
		print(e)
		return False

"""
This function gathers information from the ACI to build a network 
inventory report. If an error ocurrs, it returns False.
"""
def get_aci_info(aci_address, aci_username, aci_password):
	# Authenticate to the API
	token = auth_aci(aci_address, aci_username, aci_password)
	# Debugging information
	#print(f'APIC-cookie={token}')
	
	# Error handling
	if not token:
		print(f'Unable to authenticate to {aci_address}')
		return False

	cookies = {'APIC-cookie' : token}

	# Building URLs
	fabric_url = f'https://{aci_address}/api/node/class/fabricNode.json'
	firmware_url = 'https://{aci_address}/api/node/class/{node_dn}/firmwareRunning.json'
	uptime_url = 'https://{aci_address}/api/node/class/{node_dn}/topSystem.json'
	
	# Make HTTP GET request	
	fabricNode = requests.get(fabric_url, cookies=cookies, verify=False)
	
	# Debugging information
	#print(f'fabricNode status: {fabricNode.status_code}')
	#print(f'fabricNode body: {fabricNode.text}')

	# Proccess the data and return a list of tuples
	inventory = []
	software_version = ''
	uptime = ''

	if fabricNode.status_code != 200:
		print('Error: Failed to get fabricNode information')
		return False
	else:
		# Loop over each node in the fabric
		nodes = fabricNode.json()['imdata']
		for node in nodes:
			hostname = node['fabricNode']['attributes']['name']
			model = node['fabricNode']['attributes']['model']
			serial_number = node['fabricNode']['attributes']['serial']
			dn = node['fabricNode']['attributes']['dn']

			# Firmware
			firmwareRunninng = requests.get(
				firmware_url.format(aci_address=aci_address, node_dn=dn),
				cookies = cookies,
				verify = False
				)
			
			# Debugging information
			#print(f'firmwareRunning status: {firmwareRunninng.status_code}')
			#print(f'firmwareRunning body: {firmwareRunninng.text}')
			
			if firmwareRunninng.status_code == 200:
				if firmwareRunninng.json()['totalCount'] != '0':
					software_version = firmwareRunninng.json()['imdata'][0]['firmwareRunning']['attributes']['version']
				else:
					software_version = 'Unknown'
			else:
				print(f'Error: Failed to get firmwareRunning information for {dn}')
			
			# Uptime
			topSystem = requests.get(
				uptime_url.format(aci_address=aci_address, node_dn=dn),
				cookies = cookies,
				verify = False
				)

			# Debugging information
			#print(f'topSystem status: {topSystem.status_code}')
			#print(f'topSystem body: {topSystem.text}')

			if topSystem.status_code == 200:
				if topSystem.json()['totalCount'] != '0':
					uptime = topSystem.json()['imdata'][0]['topSystem']['attributes']['systemUpTime']
					uptime = uptime.split(':')
					uptime = f'{uptime[0]} days, {uptime[1]} hours, {uptime[2]} minutes'
				else:
					uptime = 'Unknown'
			else:
				print(f'Error: Failed to get topSystem information for {dn}')

			inventory.append( (hostname, f'apic-{model}', software_version, uptime, serial_number) )
		return inventory

"""
This function authenticates to the SD-WAN controller.
If an error ocurrs, it returns False.
"""
def auth_sdwan(sdwan_address, sdwan_username, sdwan_password):
	# Build URL
	url = f'https://{sdwan_address}/j_security_check'

	# Credentials
	body = {
		'j_username' : sdwan_username,
		'j_password' : sdwan_password
	}

	# Make the post request
	try:
		reponse = requests.post(url, data=body, verify=False)
		# Debugging information
		#print(f'SD-WAN auth status: {reponse.status_code}')
		#print(f'SD_WAN auth body: {reponse.text}')

		if reponse.status_code == 200 and 'JSESSIONID' in reponse.cookies:
			return reponse.cookies['JSESSIONID']
		else:
			print('Bad request. Maybe wrong credentials')
			return False
	except Exception as e:
		print('Error: Authentication to SD-WAN failed')
		print(e)

"""
This function logs out of the SD-WAN controller API.
It returns True if the session ended successfully. 
If an error ocurred, it returns False
"""
def log_out_sdwan(sdwan_address, cookie):
	# Build URL
	url = f'https://{sdwan_address}/logout'

	# Make cookies dictionary
	cookies = {'JSESSIONID' : cookie}

	# Make the get request
	try:
		response = requests.get(url, cookies=cookies, verify=False)

		if response.status_code == 200:
			return True
		else:
			print('Bad request')
			return False
	except Exception as e:
		print('Error: Unable to log out of the SD-WAN controller API')
		print(e)
		return False

"""
This function gathers information from the SD-WAN to build a network 
inventory report. If an error ocurrs, it returns False.
"""
def get_sdwan_info(sdwan_address, sdwan_username, sdwan_password):
	# Authenticate to the API
	cookie = auth_sdwan(sdwan_address, sdwan_username, sdwan_password)
	# Debugging information
	#print(f'JSESSIONID: {cookie}')

	if cookie:
		# Make cookies dictionary
		cookies = {'JSESSIONID' : cookie}

		# Make headers dictionary
		headers = {'Content-Type' : 'application/json'}

		# Make HTTP GET requests
		url = f'https://{sdwan_address}/dataservice/device'
		response = requests.get(url, headers=headers, cookies=cookies, verify=False)
		# Debugging information
		#print(f'SD-WAN response status: {response.status_code}')
		#print(f'SD-WAN response body: {response.text}')

		# Log out of the SD-WAN controller API
		# Debugging information
		#print('Logging out of the SD-WAN controller API')
		#print(log_out_sdwan(sdwan_address, cookie))

		# Process the data and return a list of tuples
		inventory = []
		for device in response.json()['data']:
			hostname = device['host-name']
			model = device['device-model']
			software_version = device['version']
			uptime = device['uptime-date']	# This value comes in miliseconds

			# Making human readable uptime
			uptime = uptime/1000 # Convertion to seconds is required
			uptime = datetime.fromtimestamp(uptime) # Convertion to datetime object
			now = datetime.now() # Current datetime object
			
			delta = now - uptime # Only two attributes are available: days and seconds

			days = delta.days
			hours = delta.seconds // 3600
			minutes = (delta.seconds % 3600) // 60

			uptime = f'{days} days, {hours} hours, {minutes} minutes'

			serial_number = device['board-serial']
			inventory.append( (hostname, model, software_version, uptime, serial_number) )
		return inventory
	else:
		return False
	

"""
This function is used to look for information between two substrings
It only returns the first coincidence inside another string called 'text'.
"""
def search_between(lstring, rstring, text):
    start_position = text.index(lstring)
    end_position = text.find(rstring, start_position)
    return text[start_position + len(lstring): end_position]

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
		print(f'WARNING: Parsed {command}, but it returned empty')
	except ParserNotFound:
		print(f'WARNING: Parser for {command} is not supported in {device}')

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
	# serial number: show_inventory[hostname][output][module_name]['0/0/CPU0']['sn']
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
	# serial number: show_inventory'missing'[hostname][output][name][Chassis][serial_number]
	#	'9RDIN8H58L9'
	#
	ASA
	# software version: show_version[hostname][output]
	#	'Version 9.12(2) \n'
	# uptime: show_version[hostname][output]
	# 	'edge-firewall01 up 2 hours 58 mins\n'
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
		software_version = show_version[hostname]['output']['software_version']
		uptime = show_version[hostname]['output']['uptime']
		# show_inventory is empty
		try:
			serial_number = show_inventory[hostname]['output']['module_name']['0/0/CPU0']['sn']
		except:
			serial_number = 'N/A'
	elif device_os == 'iosxe':
		model = show_version[hostname]['output']['version']['chassis']
		software_version = show_version[hostname]['output']['version']['version']
		uptime = show_version[hostname]['output']['version']['uptime']
		# show_inventory is empty
		try:
			serial_number = show_inventory[hostname]['output']['main']['chassis'][model]['sn']
		except:
			serial_number = 'N/A'
	elif device_os == 'nxos':
		software_version = show_version[hostname]['output']['platform']['software']['system_version']
		uptime_dic = show_version[hostname]['output']['platform']['kernel_uptime']
		uptime = f"{uptime_dic['days']} days, {uptime_dic['hours']} hours, {uptime_dic['minutes']} minutes"
		try:
			serial_number = show_inventory[hostname]['output']['name']['Chassis']['serial_number']
		except:
			serial_number = 'N/A'
	elif device_os == 'asa':
		raw_output = show_version[hostname]['output']
		software_version = search_between('Software Version ', '\r\n', raw_output)
		uptime = search_between(f'{hostname} up ', '\r\n', raw_output)
		try:
			serial_number = show_inventory[hostname]['output']['Chassis']['sn']
		except:
			serial_number = 'N/A'
	elif device_os == 'ios':
		software_version = show_version[hostname]['output']['version']['version']
		uptime = show_version[hostname]['output']['version']['uptime']
		serial_number = show_version[hostname]['output']['version']['chassis_sn']
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

	# List of fields in network inventory report
	network_inventory = []

	# Read testbed filename
	parser = argparse.ArgumentParser(description='testing pyATS')
	parser.add_argument('testbed', type=str, 
		help='pyATS testbed filename')
	parser.add_argument('--aci-address', type=str, 
		help='IP addres of the APIC')
	parser.add_argument('--sdwan-address', type=str, 
		help='IP address of the SD-WAN controller')
	args = parser.parse_args()

	# Load testbed file
	print(f'Loading {args.testbed} file')
	testbed = load(args.testbed)

	# It is very common that network devices use self-signed certificates, 
	# which would stop the program from working.
	disable_warnings(exceptions.InsecureRequestWarning)

	if args.aci_address:
		print(f'\nConnecting to {args.aci_address}')
		# Read credentials from the user
		aci_username = input(f'What is the username for {args.aci_address}? ')
		aci_password = getpass(f'Enter the password (input will be hidden): ')
	
		print('Making API calls')
		aci_info = get_aci_info(args.aci_address, aci_username, aci_password)

		# Debugging information
		#print(aci_info)

		# Merging aci_info with network_inventory
		network_inventory += aci_info
	
	if args.sdwan_address: 
		print(f'\nConnecting to {args.sdwan_address}')
		# Read credentials from the user
		sdwan_username = input(f'What is the username for {args.sdwan_address}? ')
		sdwan_password = getpass(f'Enter the password (input will be hidden): ')

		print('Making API calls')
		sdwan_info = get_sdwan_info(args.sdwan_address, sdwan_username, sdwan_password)

		# Debugging information
		#print(sdwan_info)
		
		# Merging sdwan_info with network_inventory 
		network_inventory += sdwan_info

	# Connect to all devices, but silent logs
	print(f'\nConnecting to all devices in {testbed.name}')
	testbed.connect(log_stdout=False)

	# testbed.devices = { hostname : <Device object> }
	for device in testbed.devices.values():
		# Run commands to gather information from network device
		show_version[device.name] = parse_command(device,'show version')
		# pprint(show_version)
		show_inventory[device.name] = parse_command(device, 'show inventory')
		# pprint(show_inventory)

		# Build network inventory
		#print(get_inventory(device, show_version, show_inventory))
		network_inventory.append(get_inventory(device, show_version, show_inventory))
		
		# Disconnect from device
		device.disconnect()
		print(f'Disconnected successfully from {device.name}')


	# Network inventory output filename
	now = datetime.now()
	inventory_filename = f'{now.strftime("%Y-%m-%d-%H-%M-%S")}_{testbed.name}_inventory.csv'

	# Write to a CSV file
	print(f'Writing to {inventory_filename}')

	with open(inventory_filename, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile, dialect='excel')
		writer.writerow(('device_name', 'device_os', 'software_version', 'uptime', 'serial_number'))

		for device_info in network_inventory:
			writer.writerow(device_info)
