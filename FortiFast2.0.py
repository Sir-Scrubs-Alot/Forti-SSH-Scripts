import paramiko
import cmd
import time
import sys
import datetime
import re
import customtkinter
from CTkMessagebox import CTkMessagebox

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

root = customtkinter.CTk()
root.geometry("1000x700")

def login():
    try:
        # Code to be executed when the button is clicked
        CTkMessagebox(title="Info", message="Starting Script!")
        fortigatehostname = fortigatehostname_entry.get()
        fortipassword = fortipassword_entry.get()
        wan1publicip = wan1publicip_entry.get()
        wan1subnet = wan1subnet_entry.get()
        ispgateway = ispgateway_entry.get()
        ipofauvikcollector = ipofauvikcollector_entry.get()
        snmpdescription = fortigatehostname
        rocommunitystring = rocommunitystring_entry.get()
        phonesystem = phonesystem_checkbox.get()
        
        if phonesystem == 1:
            allworxpublicvip = allworxpublicvip_entry.get()
            allworxprivateip = allworxprivateip_entry.get()
            # localnetworkinterface = input('Local Network Interface Name Example: lan):\n')

        # Create Variable containing the input values. This will be added to the top of the log file.
        input_values = f"fortigatehostname = {fortigatehostname}\nfortipassword = {fortipassword}\nwan1publicip = {wan1publicip}\nwan1subnet = {wan1subnet}\nispgateway = {ispgateway}\nipofauvikcollector = {ipofauvikcollector}\nsnmpdescription = {snmpdescription}\nrocommunitystring = {rocommunitystring}\nphonesystem = {phonesystem}\n\n"

        # Variables for creating Log file
        time_now  = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
        log_name = ('New_Fortigate_Script_Log_'+ fortigatehostname + '_' + time_now + '.txt')
        log_name_with_quotes = f'"{log_name}"'
        
        buff = ''
        resp = ''

        # Login using SSH, the default Fortigate IP Address, the default username and no password
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('192.168.1.99', username='admin', password='')
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        chan = ssh.invoke_shell()

        # turn off paging
        chan.send('terminal length 0\n')
        time.sleep(1)
        resp = chan.recv(99999)
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

        # FIND THE DEFAULT INTERNAL INTERFACE NAME

        # Grep for internal interface on the fortigate
        chan.send('get system interface | grep 192.168.1.99\n')
        time.sleep(3)

        # Output the bytes to a variable
        if chan.recv_ready():
            intoutput = chan.recv(5000)

        # Convert the variable to a string
        outputstring = str(intoutput)

        # Search for the internal interface name found between name and mode
        m = re.search('name: (.+?)   mode:', outputstring)
        if m:
            found = m.group(1)
            localnetworkinterface = found
        else:
            print("Internal Interface Name not Found")
            print("ABORTING SCRIPT")
            sys.exit()

            
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
        chan.send('edit ' + localnetworkinterface)
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


        # Create BBQ&Guns Address
        chan.send('config firewall address')
        chan.send('\n')
        chan.send('edit "BBQ&Guns"')
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

        # Create Friendly Countries Address Group and add BBQ&Guns to it
        chan.send('config firewall addrgrp')
        chan.send('\n')
        chan.send('edit "Friendly Countries"')
        chan.send('\n')
        chan.send('set member "BBQ&Guns"')
        chan.send('\n')
        chan.send('set color 3')
        chan.send('\n')
        chan.send('next')
        chan.send('\n')
        chan.send('end')
        chan.send('\n')
        time.sleep(1)

        if phonesystem == 1:
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



            
        # Save all of the recieved bytes to a variable
        resp = chan.recv(99999)

        # Decode the byte-like object into a string object, split it into a comma seperated string, then join the string variable. Output the results into IDLE
        output = resp.decode('ascii').split(',')
        print (''.join(output))


        # Safe the decoded string into the text file
        with open(log_name, "w") as external_file:
            external_file.write(input_values)
            print ((''.join(output)), file=external_file)
            external_file.close()


        # Disable Sip ALG. Need to do this after the output has already been put onto the log file, then append to said log file. 
        if phonesystem == 1:
            # Get the sip alg edit number
            chan.send('config system console')
            chan.send('\n')
            chan.send('set output standard')
            chan.send('\n')
            chan.send('end')
            chan.send('\n')
            chan.send('config system session-helper')
            chan.send('\n')
            chan.send('show\n')
            chan.send('\n')
            chan.send('end')
            chan.send('\n')
            time.sleep(2)

            # Output the bytes to a variable
            if chan.recv_ready():
                sipoutput = chan.recv(5000)

            # Convert the byte string to a regular string
            output_string = sipoutput.decode()

            # Find the index of the last occurrence of "edit" before "sip"
            index = output_string.rfind("edit", 0, output_string.find("sip"))

            # Extract the edit number
            sipgalgnumber = output_string[index+5:output_string.find("\r\n", index)]

            print(sipgalgnumber)
            

            # Remove the session helper
            chan.send('config system session-helper')
            chan.send('\n')
            chan.send('delete ' + sipgalgnumber)
            chan.send('\n')
            chan.send('end')
            chan.send('\n')
            time.sleep(1)
            

            # Change the default -voip -alg-mode
            chan.send('config system settings')
            chan.send('\n')
            chan.send('set default-voip-alg-mode kernel-helper-based')
            chan.send('\n')
            chan.send('set sip-expectation disable')
            chan.send('\n')
            chan.send('set sip-nat-trace disable')
            chan.send('\n')
            chan.send('end')
            chan.send('\n')
            time.sleep(1)

            # Save all of the recieved bytes to a variable
            resp = chan.recv(99999)

            # Decode the byte-like object into a string object, split it into a comma seperated string, then join the string variable. Output the results into IDLE
            output = resp.decode('ascii').split(',')
            print (''.join(output))


            # Safe the decoded string into the text file
            with open(log_name, "a") as external_file:
                print ((''.join(output)), file=external_file)
                external_file.close()

            ssh.close()

            CTkMessagebox(title="Results", message="Done!")

            
    except Exception as e:
        # Catch any exception that may occur and display an error message
        CTkMessagebox(title="Info", message=f"Button click failed: {e}")
    
            
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

def phonesystemthing():
    print(phonesystem)

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="FortiFAST", font=("Roboto", 24))
label.pack(pady=12, padx=10)



fortigatehostname_label = customtkinter.CTkLabel(master=frame,text="Enter Hostname:",font=("Roboto", 16))
fortigatehostname_label.place(x=10, y=150)

fortigatehostname_entry = customtkinter.CTkEntry(master=frame, placeholder_text="EX: ECMSI_FGT60F")
fortigatehostname_entry.place(x=150, y=150)




fortipassword_label = customtkinter.CTkLabel(master=frame,text="Enter Password:",font=("Roboto", 16))
fortipassword_label.place(x=10, y=190)

fortipassword_entry = customtkinter.CTkEntry(master=frame, placeholder_text="")
fortipassword_entry.place(x=150, y=190)



wan1publicip_label = customtkinter.CTkLabel(master=frame,text="WAN1 Public IP:",font=("Roboto", 16))
wan1publicip_label.place(x=10, y=230)

wan1publicip_entry = customtkinter.CTkEntry(master=frame, placeholder_text="")
wan1publicip_entry.place(x=150, y=230)


wan1subnet_label = customtkinter.CTkLabel(master=frame,text="WAN1 Subnet Mask:",font=("Roboto", 16))
wan1subnet_label.place(x=10, y=270)

wan1subnet_entry = customtkinter.CTkEntry(master=frame, placeholder_text="EX: 255.255.255.255")
wan1subnet_entry.place(x=150, y=270)



ispgateway_label = customtkinter.CTkLabel(master=frame,text="ISP Gateway IP:",font=("Roboto", 16))
ispgateway_label.place(x=10, y=310)

ispgateway_entry = customtkinter.CTkEntry(master=frame, placeholder_text="")
ispgateway_entry.place(x=150, y=310)



ipofauvikcollector_label = customtkinter.CTkLabel(master=frame,text="Auvik Collector IP:",font=("Roboto", 16))
ipofauvikcollector_label.place(x=10, y=350)

ipofauvikcollector_entry = customtkinter.CTkEntry(master=frame, placeholder_text="")
ipofauvikcollector_entry.place(x=150, y=350)




rocommunitystring_label = customtkinter.CTkLabel(master=frame,text="SNMP Community:",font=("Roboto", 16))
rocommunitystring_label.place(x=10, y=390)

rocommunitystring_entry = customtkinter.CTkEntry(master=frame, placeholder_text="")
rocommunitystring_entry.place(x=150, y=390)



phonesystem_checkbox = customtkinter.CTkCheckBox(master=frame, text="Allworx Phone System Setup",font=("Roboto", 16))
phonesystem_checkbox.place(x=10, y=470)



allworxpublicvip_label = customtkinter.CTkLabel(master=frame,text="Allworx Public IP:",font=("Roboto", 16))
allworxpublicvip_label.place(x=10, y=510)

allworxpublicvip_entry = customtkinter.CTkEntry(master=frame, placeholder_text="")
allworxpublicvip_entry.place(x=150, y=510)



allworxprivateip_label = customtkinter.CTkLabel(master=frame,text="Allworx Private IP:",font=("Roboto", 16))
allworxprivateip_label.place(x=10, y=550)

allworxprivateip_entry = customtkinter.CTkEntry(master=frame, placeholder_text="")
allworxprivateip_entry.place(x=150, y=550)



button = customtkinter.CTkButton(master=frame, text="Login", command=login)
button.pack(side=customtkinter.BOTTOM, padx=10,  pady=10)

'''
phonebutton = customtkinter.CTkButton(master=frame, text="Output", command=phonesystemthing)
phonebutton.pack(side=customtkinter.BOTTOM, padx=10,  pady=10)

# Create a Label widget
label=Label(win, text="", font=('Calibri 15'))
label.pack()
'''

def button_event():
    CTkMessagebox(title="Info", message="This is a CTkMessagebox!")

button = customtkinter.CTkButton(master=root, text="CTkButton", command=button_event)
button.pack(padx=20, pady=10)


root.mainloop()
