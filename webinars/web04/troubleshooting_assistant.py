"""
This script is designed to be run on NS-OX switches whose software versions is 
lower than 9.3(5). It executes several show commands to gather troubleshooting
information. The output from each command is stored on a separate file under a
timestamped folder.

Commands to run:
	show interface ethernet {ID}
	show logging last 50
	show ip arp vrf all
	show mac address-table
	show ip route vrf all
	show system internal interface ethernet {ID} ethernet {ID} event-history

	*NOTE: {ID} is read from command line arguments.

It is supposed to be run whenever an ethernet interface goes down or comes up. 
"""

from cli import cli, clid
from cli import structured_output_not_supported_error
from datetime import datetime
from os import mkdir

"""
This function gathers both raw and JSON data. It returns the result as a tuple.
"""
def run_command(command, interface):
	raw_data = cli(command.format(id=interface))

	# Not all commands are supported by clid
	try:
		json_data = clid(command.format(id=interface))
	except Exception as e:
		json_data = False
	
	return raw_data, json_data



if __name__ == '__main__':
	import argparse

	# Read command line arguments
	parser = argparse.ArgumentParser(description='Troubleshooting assistant')
	parser.add_argument('--ethernet', metavar='ID', required=True, type=str, 
		help='Ethernet interface ID')
	args = parser.parse_args()

	# Create a dictionary of commands. The key is used as filename.
	commands = {
		'show_interface' : 'show interface ethernet {id}',
		'show_logging' : 'show logging last 50',
		'show_ip_arp' : 'show ip arp vrf all',
		'show_mac_address_table' : 'show mac address-table',
		'show_ip_route' : 'show ip route vrf all',
		'show_system_internal_interface' : 'show system internal interface ethernet {id} ethernet {id} event-history'
		}

	# Create a dictionary to store the output of each command.
	output = {}

	# Execute troubleshooting commands and store the output
	print ('Running commands...')
	for filename, command in commands.items():
		output[filename] = run_command(command, args.ethernet)
		# Debugging information
		#print(run_command(command, args.ethernet))
	
	# Create a timestamp
	now = datetime.now()
	timestamp = now.strftime('%Y_%m_%d_%H_%M_%S')

	# Create a timestamped folder
	folder_name = '/bootflash/{timestamp}_ethernet_{id}_report'.format(
		timestamp=timestamp,
		id=args.ethernet.replace('/','_')
		)

	print(folder_name)
	mkdir(folder_name)
	# Write the output of each command on a separate file