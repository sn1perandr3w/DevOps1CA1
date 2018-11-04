#!/usr/bin/env python3

"""
##############################
Author: Andrew Bates
Student No: 20075908
##############################
Python3 script to:
-Create an Amazon ec2 instance
-Install Nginx and MariaDB
-Create an S3 bucket and upload an image to it
-Edit the Index.html of the Nginx homepage to display and allow a user to download said image.
-Monitor the running of both Nginx and MariaDB
##############################
How to use:
-Ensure user details for ec2 are set up on machine running script.
-Ensure provided Python3 monitoring scripts as well as images are all in the same directory as this script.
-Run script in Python3 using two arguments 
-The first argument is the name of the key file (DO NOT INPUT EXTENSION)
-The second argument is the name of the image to be copied to the bucket for use with Nginx.
-EXAMPLE:
-python3 run_newwebserver.py KEYNAME IMAGENAME.IMAGEEXTENSION
-Wait for script to run to completion

##############################
References:
-Code based on code provided by: Jimmy McGibney (Jmcgibney@wit.ie)
##############################

"""


import time
import boto3
import subprocess
import sys
import datetime
s3 = boto3.resource("s3")

key = sys.argv[1]
objectToPut = sys.argv[2]

"""
Bucket name is determined by time to ensure uniqueness.
"""
bucketName = datetime.datetime.now().strftime("%I%s%d")


"""
##############################
Sets up the instance, sets up Nginx and MariaDB calls copyCheckWebserver 
##############################
"""
def startInstance():
	try:	
		print("BUCKET NAME = " + bucketName)
		ec2 = boto3.resource('ec2')
		instance = ec2.create_instances(
	    		ImageId='ami-0c21ae4a3bd190229',
	    		KeyName= key,                                # my key name
	    		MinCount=1,
	    		MaxCount=1,
	    		SecurityGroupIds=['sg-09da3eab480312a72'],    # my HTTP/SSH sec group
	    		UserData='''#!/bin/bash

				        yum update -y
				        yum install python3 -y
		 		       amazon-linux-extras install nginx1.12 -y
					yum install -y mariadb-server
		 		       service nginx start
					systemctl start mariadb
		   		     touch /home/ec2-user/testfile''',  # to check all ok
	    		InstanceType='t2.micro')

		print ("An instance with ID", instance[0].id, "has been created.")
		time.sleep(5)
		instance[0].reload()
		print ("Public IP address:", instance[0].public_ip_address)
		instanceIP = instance[0].public_ip_address
		print("Instance IP = ", instanceIP)
		copyCheckWebserver(instanceIP)

	except Exception as error:
		print ("##########ERROR(startInstance)##########")
		print (error)
		
"""
##############################
Copies the Python script using SCP for checking if Nginx is running
and calls copyCheckMariaDB
##############################
"""
def copyCheckWebserver(instanceIP):
	try:
		IP = instanceIP
		cmdBase = 'scp -o StrictHostKeyChecking=no -i '+ key +'.pem check_webserver.py ec2-user@'
		cmd = "".join((cmdBase, IP))
		append = ":."
		cmdComp = "".join((cmd,append))
		print ("Command to SCP = ", cmdComp)
		subprocess.run(cmdComp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		copyCheckMariaDB(IP)

	except Exception as error:
		print ("##########ERROR(copyCheckWebserver)##########")
		print (error)


"""
##############################
Copies the Python script using SCP for checking if MariaDB is running
and calls chngNginxPythonPermissions
##############################
"""
def copyCheckMariaDB(instanceIP):
	try:
		IP = instanceIP
		cmdBase = 'scp -o StrictHostKeyChecking=no -i '+ key +'.pem check_mariadb.py ec2-user@'
		cmd = "".join((cmdBase, IP))
		append = ":."
		cmdComp = "".join((cmd,append))
		print ("Command to SCP = ", cmdComp)
		subprocess.run(cmdComp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		chngNginxPythonPermissions(IP)
	except Exception as error:
		print ("##########ERROR(copyCheckMariaDB)##########")
		print (error)

"""
##############################
Changes Permission of check_webserver.py
and calls chngMariaDBPythonPermissions
##############################
"""
def chngNginxPythonPermissions(instanceIP):
	try:
		IP = instanceIP
		cmdBase = 'ssh -t -o StrictHostKeyChecking=no -i '+ key +'.pem ec2-user@'
		cmd = "".join((cmdBase, IP))
		append = " 'chmod +x check_webserver.py'"
		cmdComp = "".join((cmd,append))
		print ("Command to SSH = ", cmdComp)
		subprocess.run(cmdComp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print("PERMISSIONS CHANGED")
		chngMariaDBPythonPermissions(IP)
	except Exception as error:
		print ("##########ERROR(chngPythonPermissions)##########")
		print (error)

"""
##############################
Changes Permission of check_mariadb.py
and calls chngHTMLPermissions
##############################
"""
def chngMariaDBPythonPermissions(instanceIP):
	try:
		IP = instanceIP
		cmdBase = 'ssh -t -o StrictHostKeyChecking=no -i '+ key +'.pem ec2-user@'
		cmd = "".join((cmdBase, IP))
		append = " 'chmod +x check_mariadb.py'"
		cmdComp = "".join((cmd,append))
		print ("Command to SSH = ", cmdComp)
		subprocess.run(cmdComp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print("PERMISSIONS CHANGED")
		chngHTMLPermissions(IP)
	except Exception as error:
		print ("##########ERROR(chngPythonPermissions)##########")
		print (error)

"""
##############################
Changes Permission of the Index.html file displayed by Nginx
and call setupBucket
##############################
"""
def chngHTMLPermissions(instanceIP):
	try:
		print("Sleeping for 60 seconds to allow Python/Nginx/MariaDB to finish installing")
		time.sleep(60)
		print("Sleep over.")
		IP = instanceIP
		cmdBase = 'ssh -t -o StrictHostKeyChecking=no -i '+ key +'.pem ec2-user@'
		cmd = "".join((cmdBase, IP))
		append = " 'sudo chmod 777 /usr/share/nginx/html/index.html'"
		cmdComp = "".join((cmd,append))
		print ("Command to SSH = ", cmdComp)
		subprocess.run(cmdComp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print("INDEXPERMISSIONS CHANGED")
		setupBucket(IP)
	except Exception as error:
		print ("##########ERROR(chngHTMLPermissions)##########")
		print (error)


"""
##############################
Sets up the S3 bucket, uploads the image to it and sets it to be readable by the public
and calls setupNginxHTML
##############################
"""
def setupBucket(instanceIP):
	try:
		IP = instanceIP
		print(bucketName)
		response = s3.create_bucket(Bucket=bucketName, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
		print("BUCKET CREATE RESPONSE:")
		print (response)
		response = s3.Object(bucketName, objectToPut).put(Body=open(objectToPut, 'rb'), ACL = 'public-read')
		print("BUCKET PUT RESPONSE:")
		print (response)
		setupNginxHTML(IP)
	except Exception as error:
		print ("##########ERROR(setupBucket)##########")
		print (error)

"""
##############################
Writes the appropriate HTML to Index.html, allowing for display and download of the image
and calls runCheckWebServer and runCheckMariaDB
##############################
"""
def setupNginxHTML(instanceIP):
	try:
		IP = instanceIP
		cmdBase = 'ssh -i '+ key +'.pem ec2-user@'
		cmd = "".join((cmdBase, IP))
		append = """ "echo '<html> <img src="https://s3-eu-west-1.amazonaws.com/"""+bucketName+"""/"""+objectToPut+""""> <br><p>To download the uploaded S3 image click</p><a href="https://s3-eu-west-1.amazonaws.com/"""+bucketName+"""/"""+objectToPut+"""">HERE</a></html>' > /usr/share/nginx/html/index.html"  """
		cmdComp = "".join((cmd,append))
		print ("Command to SSH = ", cmdComp)
		subprocess.run(cmdComp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print("####################")
		runCheckWebServer(IP)
		print("####################")
		runCheckMariaDB(IP)
		print("####################")
		print("Webpage with bucket image should be available at " + IP)
		print("Check it out, have a nice day and thank you for your patience as everything installed!")
	except Exception as error:
		print ("##########ERROR(setupNginxHTML)##########")
		print (error)

"""
##############################
Runs python script to check for Nginx
##############################
"""
def runCheckWebServer(instanceIP):
	try:
		IP = instanceIP
		cmdBase = 'ssh -i '+ key +'.pem ec2-user@'
		cmd = "".join((cmdBase, IP))
		append = " 'python3 check_webserver.py'"
		cmdComp = "".join((cmd,append))
		print ("Command to SSH = ", cmdComp)
		
		p = subprocess.run(cmdComp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print(p.stdout.strip())
	except Exception as error:
		print ("##########ERROR(runCheckWebServer)##########")
		print (error)

"""
##############################
Runs python script to check for Mariadb
##############################
"""
def runCheckMariaDB(instanceIP):
	try:
		IP = instanceIP
		cmdBase = 'ssh -i '+ key +'.pem ec2-user@'
		cmd = "".join((cmdBase, IP))
		append = " 'python3 check_mariadb.py'"
		cmdComp = "".join((cmd,append))
		print ("Command to SSH = ", cmdComp)
		
		p = subprocess.run(cmdComp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print(p.stdout.strip())
	except Exception as error:
		print ("##########ERROR(runCheckMariaDB)##########")
		print (error)

# Define a main() function.
def main():	
    startInstance()
      
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

