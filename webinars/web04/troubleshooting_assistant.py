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

from cli import cli

if __name__ == '__main__':
	import argparse

	# Read command line arguments
	parser = argparse.ArgumentParser(description='Troubleshooting assistant')
	parser.add_argument('--ethernet', required=True, type=str, 
		help='Ethernet interface ID')
	args = parser.parse_args()

	# Execute troubleshooting commands and store the output
	print ('Testing python library')

	r = cli('show interface ethernet {id}'.format(id=args.ethernet))
	print(r)
	# Create a timestamped folder 

	# Write the output of each command on a separate file