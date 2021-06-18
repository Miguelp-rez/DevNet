# Webinar 03: Software Defined Network Inventory  

## Objectives

1. Generate an inventory in spreadsheet format.
2. Gather data about the switches, routers, and firewalls deployed in the network.
3. Include: device name, software version, uptime and serial numbers.
4. include devices from the ACI and SD-WAN

## Topology

Reserve the Cisco NSO [sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) 
to access all network devices in this lab.

![Topology](/webinars/web01/topology.PNG)

## Software requirements

I used Ubuntu 20.04 LTS, but any other Linux host should work. 
With regards to python, versions 3.8 or 3.7 are good choices in summer 2021.  
Download and install [postman](https://www.postman.com/downloads/)


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

Authenticate to the API

    POST https://sandboxapicdc.cisco.com/api/aaaLogin.json

In the body include the credentials

    {
        "aaaUser": {
            "attributes" : {
                "name" : "admin",
                "pwd" : "ciscopsdt"
            }
        }
    }

Make the following API calls with postman.

	GET https://sandboxapicdc.cisco.com/api/node/class/fabricNode.json
    GET https://sandboxapicdc.cisco.com/api/node/class/topology/pod-1/topSystem.json
    GET https://sandboxapicdc.cisco.com/api/mo/topology/pod-1/node-101.json?query-target=children&target-subtree-class=topSystem

