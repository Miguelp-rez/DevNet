# Webinar 04: Building a Troubleshooting Assistant  

## Objectives

1. Watch for operational state changes of an Ethernet interface on a Nexus 9000 switch.
2. When the interface goes down (or up), execute several show commands.
3. Write the output of each command to a separate file
3. Create a timestamped folder to store all the log files from the same event.

## Topology

Reserve the Cisco NSO [sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) 
to access all network devices in this lab.

![Topology](/webinars/web04/topology.PNG)

## Software requirements

I used Ubuntu 20.04 LTS, but any other Linux host should work. 
With regards to python, NX-OS switches with software version 9.3(5) or greater come with python 3. Earlier versions use python 2.7.  

## Activities

For this lab, it is better to run the script directly on the switch. 

Log into the switch.
    
    telnet 10.10.20.177

Use the interactive python shell to see if things work manually.
    
    Switch# python

Import the cisco CLI library.
    
    from cli import cli

Execute the following show commands.
    
    cli('show interface ethernet #/#')
    cli('show logging last 50')
    cli('show ip arp vrf all')
    cli('show mac address-table')
    cli('show ip route vrf all')
    cli('show system internal interface ethernet #/# ethernet #/# event-history')

Enable scp on the switch, so you can transfer the script from your workstation to the device bootflash.
    
    feature scp-server 

Copy the file to the switch after each update.
    
    scp troubleshooting_assistant.py cisco@10.10.20.177:

Run the script.
    
    Switch# python bootflash:troubleshooting_assistant.py