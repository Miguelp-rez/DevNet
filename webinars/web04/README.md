# Webinar 04: Building a Troubleshooting Assistant  

## Objectives

1. Watch for operational state changes of an Ethernet interface on a Nexus 9000 switch.
2. When the interface goes down (or up), execute several show commands.
3. Write the output of each command to a separate file
4. Create a timestamped folder to store all the log files from the same event.
5. Use EEM to run the script everytime the interface goes down (or up).

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
    
    dist-sw01# python

Import the cisco CLI library.
    
    from cli import cli

Execute the following show commands.
    
    cli('show interface ethernet 1/3')
    cli('show logging last 50')
    cli('show ip arp vrf all')
    cli('show mac address-table')
    cli('show ip route vrf all')
    cli('show system internal interface ethernet 1/3 ethernet 1/3 event-history')

Enable scp on the switch, so you can transfer the script from your workstation to the device bootflash.
    
    dist-sw01(config)# feature scp-server 

Copy the file to the switch.
    
    scp troubleshooting_assistant.py cisco@10.10.20.177:

Run the script.
    
    dist-sw01# python bootflash:troubleshooting_assistant.py

#### EEM
Enable logging to the terminal.

    dist-sw01# terminal monitor

Shutdown ethernet 1/3 interface. Look at the syslog messages generated.

    dist-sw01(config)# int eth 1/3
    dist-sw01(config-if)# shut
    dist-sw01(config-if)# 2021 Jul  5 17:27:50 dist-sw01 %ETHPORT-5-IF_DOWN_CFG_CHANGE: Interface Ethernet1/3 is down(Config change)
    2021 Jul  5 17:27:50 dist-sw01 %ETHPORT-5-IF_DOWN_ADMIN_DOWN: Interface Ethernet1/3 is down (Administratively down)

Enable ethernet 1/3 interface. Look at the syslog messages generated.

    dist-sw01(config-if)# no shut
    dist-sw01(config-if)# 2021 Jul  5 17:40:10 dist-sw01 %ETHPORT-5-IF_ADMIN_UP: Interface Ethernet1/3 is admin up .
    2021 Jul  5 17:40:10 dist-sw01 %ETHPORT-5-SPEED: Interface Ethernet1/3, operational speed changed to auto
    2021 Jul  5 17:40:10 dist-sw01 %ETHPORT-5-IF_DUPLEX: Interface Ethernet1/3, operational duplex mode changed to unknown
    2021 Jul  5 17:40:10 dist-sw01 %ETHPORT-5-IF_RX_FLOW_CONTROL: Interface Ethernet1/3, operational Receive Flow Control state changed to off
    2021 Jul  5 17:40:10 dist-sw01 %ETHPORT-5-IF_TX_FLOW_CONTROL: Interface Ethernet1/3, operational Transmit Flow Control state changed to off
    2021 Jul  5 17:40:10 dist-sw01 %ETHPORT-5-IF_UP: Interface Ethernet1/3 is up in Layer3

Create an EEM applet to monitor for interface ethernet 1/3 going down.

    dist-sw01(config)# event manager applet Eth_13_down
    dist-sw01(config-applet)# event syslog pattern "Interface Ethernet1/3 is down"
    dist-sw01(config-applet)# action 1 syslog priority notifications msg Saw interface Eth 1/3 go down

Create an EEM applet to monitor for interface ethernet 1/3 coming up.

    dist-sw01(config)# event manager applet Eth_13_up
    dist-sw01(config-applet)# event syslog pattern "Interface Ethernet1/3 is up"
    dist-sw01(config-applet)# action 1 syslog priority notifications msg Saw interface Eth 1/3 come up

Cause interface ethernet 1/3 to change its operational state.
    
    dist-sw01(config)# interface eth 1/3
    dist-sw01(config)# shutdown
    dist-sw01(config)# no shutdown

**NOTE**: The script takes around 14s to complete.

Download all report files to your workstation

    scp -r cisco@10.10.20.177:*_ethernet_1_3_report ./