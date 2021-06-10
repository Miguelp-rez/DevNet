# Webinar 01: Automating a network inventory with Python  

## Objectives

1. Generate an inventory in spreadsheet format.
2. Gather data about the switches, routers, and firewalls deployed in the network.
3. Include: device name, software version, uptime and serial numbers.

## Activities

Create a python virtual environment.

    python3 -m venv venv
    source venv/bin/activate

Install all the modules required for this exercise.

    pip install MarkupSafe==1.1.1
    pip install wheel
    pip install pyats pyats.contrib genie

Create a testbed file from the inventory spreadsheet.

    pyats create testbed file\
     --path nso_sandbox_devices.xlsx\
     --output nso_sandbox_testbed.yaml

Verify if pyATS commands work correctly.

	pyats parse 'show version'\
	 --testbed nso_sandbox_testbed.yaml
	pyats parse 'show inventory'\
	 --testbed nso_sandbox_testbed.yaml

NOTE: At the time of this writing there is not a parser for the 'show version' 
command in ASA devices. Also, in some devices the 'show inventory' command was  
parsed correctly, but it returned empty.