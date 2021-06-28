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

#### Environment

Create a python virtual environment.

    python3 -m venv venv
    source venv/bin/activate

Install all the modules required for this exercise.

    pip install MarkupSafe==1.1.1
    pip install wheel
    pip install pyats pyats.contrib genie
    pip install requests

Create a testbed file from the inventory spreadsheet.

    pyats create testbed file\
     --path nso_sandbox_devices.xlsx\
     --output nso_sandbox_testbed.yaml

#### ACI

Authenticate to the API.

    POST https://sandboxapicdc.cisco.com/api/aaaLogin.json

Include the following credentials in the body of the POST request.

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
    GET https://sandboxapicdc.cisco.com/api/node/class/firmwareRunning.json
    GET https://sandboxapicdc.cisco.com/api/node/class/topSystem.json

You can include the dn of a node in the URI to only get datails of that object.

    GET https://sandboxapicdc.cisco.com/api/node/class/topology/pod-1/node-101/firmwareRunning.json
    GET https://sandboxapicdc.cisco.com/api/node/class/topology/pod-1/node-101/topSystem.json

Similarly, you can use query filters to get equivalent results.

    GET https://sandboxapicdc.cisco.com/api/node/mo/topology/pod-1/node-101.json?query-target=subtree&target-subtree-class=firmwareRunning
    GET https://sandboxapicdc.cisco.com/api/node/mo/topology/pod-1/node-101.json?query-target=children&target-subtree-class=topSystem

#### SD-WAN

Authenticate to the API. The Sandbox is currently running vManage 19.2, so only the jsessionid cookie is needed.

    POST https://sandbox-sdwan-1.cisco.com/j_security_check
    Content-Type: application/x-www-form-urlencoded  

Include the following credentials in the body of the POST request.

    j_username=devnetuser
    j_password=RG!_Yw919_83

Make the following API call.

    GET https://sandbox-sdwan-1.cisco.com/dataservice/device
    Content-Type: application/json

Log out after finishing the API requests.

    GET https://sandbox-sdwan-1.cisco.com/logout