# https://appdividend.com/2021/06/21/how-to-read-file-into-list-in-python/
# https://www.w3schools.com/python/python_lists_loop.asp
# https://stackoverflow.com/questions/49777888/pass-python-variable-inside-command-with-paramiko
# https://network-knowledge.work/fortigate-interface-cli/
import paramiko
import cmd
import time
import sys

connectionip = input('IP to SSH to:\n')
fortiusername = input('Fortigate Username:\n')
fortipassword = input('Fortigate Password:\n')
wan1publicip = input('Wan1 Public IP:\n')
wan1subnet = input('Wan1 Subnet Mask:\n')

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


# Display output of first command
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
resp = chan.recv(9999)
output = resp.decode('ascii').split(',')
print (''.join(output))



ssh.close() 
