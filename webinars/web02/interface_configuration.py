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
	print("Updating interfaces' description")
	# Load testbed file
	# Read the source of truth file
	# Create interface descriptions
	# Connect to all devices
	# Grab current interface descriptions
	# Apply new interface descriptions
	# Run cdp/lldp commands to grab neighbor information
	# Check if devices are actually connected to the interfaces listed in CSV file.
	# Disconnect from all devices
	# Update source of truth file