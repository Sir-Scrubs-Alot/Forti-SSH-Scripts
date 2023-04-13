import csv
import requests
import datetime
import os

requests.packages.urllib3.disable_warnings()

# Replace with the path to your CSV file
# csv_file_path = "firewalls-advancedsecurity.csv"
csv_file_path = "firewalls-syslogtest.csv"

# Define the column names in the CSV file
csv_columns = ["number", "companyname", "description", "ip", "username", "encoded_password", "syslogd", "syslogd2"]

# Get the current date and time
now = datetime.datetime.now()

# Create a formatted timestamp string to use in the filename
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

# Define Error Log File
error_log = f"error_log_{timestamp}.txt"
print(f"Error messages will be stored in {error_log}")

# Read the CSV file
with open(csv_file_path) as csv_file:
    reader = csv.DictReader(csv_file, fieldnames=csv_columns)
    for row in reader:
        # Extract the values from the current row
        number = row["number"]
        companyname = row["companyname"]
        description = row["description"]
        ip = row["ip"]
        username = row["username"]
        encoded_password = row["encoded_password"]
        syslogd = row["syslogd"]
        syslogd2 = row["syslogd2"]

        # Construct the payload for the login request
        payload = f"username={username}&secretkey={encoded_password}&ajax=1"
        url = f"https://{ip}/logincheck"

        try:
            # Send the login request
            response = requests.post(url, data=payload, verify=False)
            response.raise_for_status()  # Raise an error if the response status code is not 200

        except requests.exceptions.RequestException as e:
            # print(f"Failure for {number}_{companyname}_{description}")
            number_companyname_Description = f"{number}_{companyname}_{description}"
            with open(error_log, 'a') as file:
                file.write(f"{number_companyname_Description}: {str(e)}\n")
            continue

        # Write to error log if response status code is not 200
        if response.status_code != 200:
            number_companyname_Description = f"{number}_{companyname}_{description}"
            with open(error_log, 'a') as file:
                file.write(f"{number_companyname_Description}: Response Status Code:  {response.status_code}\n")
                
        
        # Write to error log if reponse text does not equal ldocument.location=
        verify = "1document.location="
        converted_response_status_code = str(response.text)
        if  verify not in converted_response_status_code:
            number_companyname_Description = f"{number}_{companyname}_{description}"
            # print (f"ERROR! {number_companyname_Description}: Response Text: {response.text}\n")
            with open(error_log, 'a') as file:
                file.write(f"{number_companyname_Description}: Response Text: {response.text}\n")

        if verify in converted_response_status_code:
            # =====================================================================================
        
            # PT 2

            csrf_token = None
            for cookie in response.cookies:

                if 'ccsrftoken' in cookie.name:
                    csrf_token = cookie.value
                    break

                
                '''
                if cookie.name == 'ccsrftoken':
                    csrf_token = cookie.value
                    break
                
                if cookie.name == 'ccsrftoken_8080':
                    csrf_token = cookie.value
                    break
                '''
                

            if csrf_token is None:
                print("CSRF token cookie not found!")
                print(response.cookies)
                print("Ending Script. Please Check csrf_token")
                number_companyname_Description = f"{number}_{companyname}_{description}"
                with open(error_log, 'a') as file:
                    file.write(f"{number_companyname_Description}: Problem with CSRF Token: {response.cookies}\n")

            if csrf_token is not None:
                
                # Cut off the begining and end quotes
                csrf_token = csrf_token[1:][:-1]

                url2 = f"https://{ip}/api/v2/cmdb/log.syslogd/setting"

                # Note: Had to use triple quotes to create a multiline string literal. This allowed us to include both double quotes and newlines without needing to escape them, as you can't have a backspace in an f-string natively
                payload2 = f'''{{\r\n    \"status\": \"enable\",\r\n    \"server\": \"{syslogd}\"\r\n  }}'''

                            

                headers2 = {
                    'X-CSRFTOKEN' : csrf_token,
                    'Content-Type': 'text/plain'
                }

                print(headers2)
                response2= requests.request("PUT", url2, headers=headers2, data=payload2, verify=False, cookies=response.cookies)

                print(response2.text)




                url3 = f"https://{ip}/api/v2/cmdb/log.syslogd2/setting"

                payload3 = f'''{{\r\n    \"status\": \"enable\",\r\n    \"server\": \"{syslogd2}\"\r\n  }}'''


                headers2 = {
                    'X-CSRFTOKEN' : csrf_token,
                    'Content-Type': 'text/plain'
                }

                print(headers2)
                response3= requests.request("PUT", url3, headers=headers2, data=payload3, verify=False, cookies=response.cookies)

                print(response3.text)
                  

csv_file.close()
