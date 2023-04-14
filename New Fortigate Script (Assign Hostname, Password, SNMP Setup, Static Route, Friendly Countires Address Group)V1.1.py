"""
Author: Nate Bair
Version: v1.1
Python Version: 3.9.6
Summary:
This script prompts the technician for several key pieces of information, before performing the following:
- Assigns a Hostname and Password to the Fortigate
- Sets a static IP and Subnet to WAN1
- Sets a static route
- Enables SNMP on the Local Network Interface
- Enables SNMP Agent
- Configures SNMP Community String on the Router and any Switches that would get connected to it
- Creates USA Address and "Friendly Countries" Address Group
- Creates a log file and dumps each command to it

Additionas:
- Prompt tech if they're installing a phone system, if y is input then they will be prompted for Allworx information, and the script will create the allworx VIP's and Policy. Note: It defaults to using 'lan' in the policy.
- Cleaned up the top comment output to the technician
"""

import paramiko
import cmd
import time
import sys
import datetime


# Prompt Technician stating what they'll need to run the script
print('Welcome to the New Fortigate Setup Script! \n Please have the following information ready:\n The WAN1 Public IP Address and Subnet Mask \n The ISP Gateway IP Address \n The IP Address of the Probe\Auvik Collector \n \n If your installing a phone system, you will also need to supply: \n The Public IP Address of the Allworx System \n The Private IP Address of the Allworx System \n Note: The Allworx Firewall Policy will use lan to wan1 by default \n')

# Begin prompting technician for input
fortigatehostname = input('Set the Hostname:\n')
fortipassword = input('Please set the Fortigate Password:\n')
wan1publicip = input('Wan1 Public IP:\n')
wan1subnet = input('Wan1 Subnet Mask:\n')
ispgateway = input('ISP Gateway:\n')
ipofauvikcollector = input('IP of Probe/Auvik Collector:\n')
snmpdescription = input('SNMP Description (use format COMPANYNAME_FGTMODEL. EX: ECMSI_FGT60E):\n')
rocommunitystring = input('SNMP Community String: \n')
phonesystem = input('Are you installing a phone system? (y/n): \n')
# lanip = input('lan IP:\n') (Current not in use)
# lansubnet = input('lan Subnet Mask:\n') (Current not in use)

if phonesystem == "y":
    allworxpublicvip = input('Allworx Public IP:\n')
    allworxprivateip = input('Allworx Private IP:\n')
    # localnetworkinterface = input('Local Network Interface Name Example: lan):\n')
    localnetworkinterface = "lan"
      
    
lastchance = input('Would you like to proceed with these settings? hit enter for yes, CTRL-C to cancel)')

# Variables for creating Log file
time_now  = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
log_name = ('New_Fortigate_Script_Log_'+ fortigatehostname + '_' + time_now + '.txt')
log_name_with_quotes = f'"{log_name}"'

buff = ''
resp = ''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.99', username='admin', password='')
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
chan = ssh.invoke_shell()

# turn off paging
chan.send('terminal length 0\n')
time.sleep(1)
resp = chan.recv(9999)
output = resp.decode('ascii').split(',')

# Assign Hostname and Password to the Fortigate
time.sleep(1)
chan.send(fortipassword)
chan.send('\n')
chan.send(fortipassword)
chan.send('\n')
chan.send(fortipassword)
chan.send('\n')
time.sleep(1)
chan.send('config system global')
chan.send('\n')
chan.send('set hostname '+ fortigatehostname)
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)

# Assign IP and Subnet to Wan1
chan.send('config system interface')
chan.send('\n')
chan.send('edit "wan1"')
chan.send('\n')
chan.send('set mode static')
chan.send('\n')
chan.send('set ip ' + wan1publicip + ' '+ wan1subnet)
chan.send('\n')
chan.send('set allowaccess ping https')
chan.send('\n')
chan.send('show')
chan.send('\n')
chan.send('next')
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)

# Set static route
chan.send('config router static')
chan.send('\n')
chan.send('edit 1')
chan.send('\n')
chan.send('set dst 0.0.0.0/0')
chan.send('\n')
chan.send('set gateway ' + ispgateway)
chan.send('\n')
chan.send('set device wan1')
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)
          
# Enable SNMP on Local Network Interface
chan.send('config system interface')
chan.send('\n')
chan.send('edit "lan"')
chan.send('\n')
chan.send('set allowaccess ping https ssh snmp http fgfm fabric')
chan.send('\n')
chan.send('set role lan')
chan.send('\n')
chan.send('next ')
chan.send('\n')
chan.send('end')
chan.send('\n')

#Enable SNMP agent
chan.send('config system snmp sysinfo')
chan.send('\n')
chan.send('set status enable')
chan.send('\n')
chan.send('set description ' + snmpdescription)
chan.send('\n')
chan.send('end')
chan.send('\n')

# Configure SNMP Community String
chan.send('config system snmp community')
chan.send('\n')
chan.send('edit 1')
chan.send('\n')
chan.send('set name "' + rocommunitystring + '"')
chan.send('\n')
chan.send('config hosts')
chan.send('\n')
chan.send('edit 1')
chan.send('\n')
chan.send('set ip ' + ipofauvikcollector + ' 255.255.255.255')
chan.send('\n')
chan.send('next')
chan.send('\n')
chan.send('end')
chan.send('\n')
chan.send('set events cpu-high mem-low log-full intf-ip vpn-tun-up vpn-tun-down ha-switch ha-hb-failure ips-signature ips-anomaly av-virus av-oversize av-pattern av-fragmented fm-if-change fm-conf-change bgp-established bgp-backward-transition ha-member-up ha-member-down ent-conf-change av-conserve av-bypass av-oversize-passed av-oversize-blocked ips-pkg-update ips-fail-open faz-disconnect wc-ap-up wc-ap-down fswctl-session-up fswctl-session-down load-balance-real-server-down device-new per-cpu-high dhcp ospf-nbr-state-change ospf-virtnbr-state-change')
chan.send('\n')
chan.send('next')
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)

# Enable SNMP on Switches
chan.send('config switch-controller snmp-community')
chan.send('\n')
chan.send('edit "1"')
chan.send('\n')
chan.send('set name ' + rocommunitystring)
chan.send('\n')
chan.send('set status enable')
chan.send('\n')
chan.send('set query-v1-status enable')
chan.send('\n')
chan.send('set query-v1-port 161')
chan.send('\n')
chan.send('set query-v2c-status enable')
chan.send('\n')
chan.send('set query-v2c-port 161')
chan.send('\n')
chan.send('set trap-v1-status enable')
chan.send('\n')
chan.send('set trap-v1-lport 162')
chan.send('\n')
chan.send('set trap-v1-rport 162')
chan.send('\n')
chan.send('set trap-v2c-status enable')
chan.send('\n')
chan.send('set trap-v2c-lport 162')
chan.send('\n')
chan.send('set trap-v2c-rport 162')
chan.send('\n')
chan.send('set events cpu-high mem-low log-full intf-ip ent-conf-change')
chan.send('\n')
chan.send('config hosts')
chan.send('\n')
chan.send('edit "10"')
chan.send('\n')
chan.send('set ip ' + ipofauvikcollector + ' 255.255.255.255')
chan.send('\n')
chan.send('end')
chan.send('\n')
chan.send('next')
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)


# Create USA Address
chan.send('config firewall address')
chan.send('\n')
chan.send('edit "USA"')
chan.send('\n')
chan.send('set type geography')
chan.send('\n')
chan.send('set country "US"')
chan.send('\n')
chan.send('set color 3')
chan.send('\n')
chan.send('next')
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)

# Create Friendly Countries Address Group and add USA to it
chan.send('config firewall addrgrp')
chan.send('\n')
chan.send('edit "Friendly Countries"')
chan.send('\n')
chan.send('set member "USA"')
chan.send('\n')
chan.send('set color 3')
chan.send('\n')
chan.send('next')
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)

if phonesystem == "y":
    # Begin configuring Allworx VIPs
    chan.send('config firewall vip')
    chan.send('\n')
    # Allworx_IP 5060_tcp
    chan.send('edit "Allworx_IP 5060_tcp"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "wan1"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set extport 5060')
    chan.send('\n')
    chan.send('set mappedport 5060')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')

    # Allworx_IP 5060_udp
    chan.send('edit "Allworx_IP 5060_udp"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "wan1"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set protocol udp')
    chan.send('\n')
    chan.send('set extport 5060')
    chan.send('\n')
    chan.send('set mappedport 5060')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')

    # Allworx_IP 15000-15511_udp
    chan.send('edit "Allworx_IP 15000-15511_udp"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "wan1"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set protocol udp')
    chan.send('\n')
    chan.send('set extport 15000-15511')
    chan.send('\n')
    chan.send('set mappedport 15000-15511')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')

    # Allworx_IP 8443_udp
    chan.send('edit "Allworx_IP 8443_udp"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "wan1"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set extport 8443')
    chan.send('\n')
    chan.send('set mappedport 8443')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')

    # Allworx_IP 8081_udp
    chan.send('edit "Allworx_IP 8081_udp"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "wan1"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set extport 8081')
    chan.send('\n')
    chan.send('set mappedport 8081')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')

    # Allworx_IP 2088_udp
    chan.send('edit "Allworx_IP 2088_udp"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "wan1"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set protocol udp')
    chan.send('\n')
    chan.send('set extport 2088')
    chan.send('\n')
    chan.send('set mappedport 2088')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')

    # Allworx_IP 443_udp
    chan.send('edit "Allworx_IP 443_udp"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "wan1"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set extport 443')
    chan.send('\n')
    chan.send('set mappedport 443')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')

    # Allworx_SMTP
    chan.send('edit "Allworx_SMTP"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "any"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set extport 25')
    chan.send('\n')
    chan.send('set mappedport 25')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')

    # Allworx_IP 16384-32767
    chan.send('edit "Allworx_IP 16384-32767"')
    chan.send('\n')
    chan.send('set extip '+ allworxpublicvip)
    chan.send('\n')
    chan.send('set mappedip "' + allworxprivateip  + '"')
    chan.send('\n')
    chan.send('set extintf "wan1"')
    chan.send('\n')
    chan.send('set portforward enable')
    chan.send('\n')
    chan.send('set protocol udp')
    chan.send('\n')
    chan.send('set extport 16384-32767')
    chan.send('\n')
    chan.send('set mappedport 16384-32767')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')
    chan.send('end')
    chan.send('\n')


    # Create Virtual IP Group
    chan.send('config firewall vipgrp')
    chan.send('\n')
    chan.send('edit Allworx')
    chan.send('\n')
    chan.send('set interface wan1')
    chan.send('\n')
    chan.send('set member Allworx_IP\ 5060_tcp Allworx_IP\ 5060_udp Allworx_IP\ 16384-32767 Allworx_SMTP Allworx_IP\ 443_udp Allworx_IP\ 2088_udp Allworx_IP\ 8081_udp Allworx_IP\ 8443_udp Allworx_IP\ 15000-15511_udp')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')
    chan.send('end')
    chan.send('\n')

    # Create Allworx Policy
    chan.send('config firewall policy')
    chan.send('\n')
    chan.send('edit 90')
    chan.send('\n')
    chan.send('set name "Allworx"')
    chan.send('\n')
    chan.send('set srcintf "wan1"')
    chan.send('\n')
    chan.send('set dstintf "' + localnetworkinterface  + '"')
    chan.send('\n')
    chan.send('set action accept')
    chan.send('\n')
    chan.send('set srcaddr "all"')
    chan.send('\n')
    chan.send('set dstaddr "Allworx"')
    chan.send('\n')
    chan.send('set schedule "always"')
    chan.send('\n')
    chan.send('set service "ALL"')
    chan.send('\n')
    chan.send('next')
    chan.send('\n')
    chan.send('end')
    chan.send('\n')
    time.sleep(1)

resp = chan.recv(99999)
output = resp.decode('ascii').split(',')
print (''.join(output))
with open(log_name, "w") as external_file:
    print ((''.join(output)), file=external_file)
    external_file.close()

'''
# Assign IP and Subnet to lan (Current not in use)
chan.send('config system interface')
chan.send('\n')
chan.send('edit "lan"')
chan.send('\n')
chan.send('set ip ' + lanip + ' '+ lansubnet)
chan.send('\n')
chan.send('set allowaccess ping https ssh')
chan.send('\n')
chan.send('show')
chan.send('\n')
chan.send('next')
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)
resp = chan.recv(9999)
output = resp.decode('ascii').split(',')
print (''.join(output))
'''

ssh.close()



'''
Web References:
https://appdividend.com/2021/06/21/how-to-read-file-into-list-in-python/
https://www.w3schools.com/python/python_lists_loop.asp
https://stackoverflow.com/questions/49777888/pass-python-variable-inside-command-with-paramiko
Allworx CLI: https://community.fortinet.com/t5/FortiGate/Technical-Tip-Virtual-IP-VIP-port-forwarding-configuration/ta-p/198143

SUBLIME:
https://stackoverflow.com/questions/39556514/sublime-text-3-how-to-edit-multiple-lines
https://gist.github.com/martincr/34f4fa08f6924512487d5b683c4fe800
'''

