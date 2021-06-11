# Webinar 02: Enforcing Interface Configuration Standards through Automation  

## Objectives

1. Configure interface descriptions on IOS, IOS XE, NX-OS, and IOS XR devices.
2. Description format: Connected to {DEVICE} {INTERFACE} – {PURPOSE}.
3. Save current description on interfaces for audit/change control.
4. Check if interfaces are actually connected to interfaces listed in CSV file.

## Topology

Reserve the Cisco NSO [sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) 
to access all network devices in this lab.

![Topology](/webinars/web02/topology.PNG)

NOTE: All information related to interface connections was provided in a CSV file.

## Software requirements

I used Ubuntu 20.04 LTS, but any other Linux host should work. 
With regards to python, versions 3.8 or 3.7 are good choices in summer 2021.


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