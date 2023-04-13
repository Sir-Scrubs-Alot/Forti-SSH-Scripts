# https://appdividend.com/2021/06/21/how-to-read-file-into-list-in-python/
# https://www.w3schools.com/python/python_lists_loop.asp
# https://stackoverflow.com/questions/49777888/pass-python-variable-inside-command-with-paramiko
# Allworx CLI: https://community.fortinet.com/t5/FortiGate/Technical-Tip-Virtual-IP-VIP-port-forwarding-configuration/ta-p/198143
# SUBLIME:
# https://stackoverflow.com/questions/39556514/sublime-text-3-how-to-edit-multiple-lines
# https://gist.github.com/martincr/34f4fa08f6924512487d5b683c4fe800
import paramiko
import cmd
import time
import sys


connectionip = input('IP to SSH to:\n')
fortiusername = input('Fortigate Username:\n')
fortipassword = input('Fortigate Password:\n')
allworxpublicvip = input('Allworx Public IP:\n')
allworxprivateip = input('Allworx Private IP:\n')
localnetworkinterface = input('Local Network Interface Name:\n')
ipofauvikcollector = input('IP of Probe/Auvik Collector:\n')
snmpdescription = input('SNMP Description (use format COMPANYNAME_FGTMODEL. EX: ECMSI_FGT60E):\n')

buff = ''
resp = ''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(connectionip, username=fortiusername, password=fortipassword)
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
chan = ssh.invoke_shell()

# turn off paging
chan.send('terminal length 0\n')
time.sleep(1)
resp = chan.recv(9999)
output = resp.decode('ascii').split(',')
#print (''.join(output))

# Enable SNMP on Local Network Interface
chan.send('config system interface')
chan.send('\n')
chan.send('edit "' + localnetworkinterface + '"')
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
chan.send('set name "ADD SNMP COMMUNITY STRING HERE"')
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
resp = chan.recv(9999)
output = resp.decode('ascii').split(',')
print (''.join(output))





'''
with open("randomfile.txt", "w") as external_file:
    print ((''.join(output)), file=external_file)
    external_file.close()
'''

'''
file = open("output.txt", "w")
file.write(a)
file.close
'''


"""
# Define a variable to NAC-Policy and MAC Address. Tested and worked!
x = "TestFromScript3"
y = "64:00:6a:53:4f:8b"
# Display output of first command
chan.send('config user nac-policy')
chan.send('\n')
chan.send('edit "' + x  + '"')
chan.send('\n')
chan.send('set mac "' + y  + '"')
chan.send('\n')
chan.send('set switch-fortilink "fortilink"')
chan.send('\n')
chan.send('set switch-mac-policy "TEST NAC"')
chan.send('\n')
chan.send('show')
chan.send('\n')
chan.send('end')
chan.send('\n')
time.sleep(1)
resp = chan.recv(9999)
output = resp.decode('ascii').split(',')
print (''.join(output))
"""



ssh.close()
#file_path = 'output.txt'
#sys.stdout = open(file_path, "w")


