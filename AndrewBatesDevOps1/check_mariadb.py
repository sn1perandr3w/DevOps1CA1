#!/usr/bin/python3

"""A reworking of the Check_Webserver script to check for
   MariaDB. Due to MariaDB using MySQL, a telltale sign that it is running is
   if mysqld is found using grep.
"""

import subprocess

def checknginx():
  try:
    cmd = 'ps -A | grep mysqld'
   
    subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("MariaDB Server IS running")
   
  except subprocess.CalledProcessError:
    print("MariaDB Server IS NOT running")
    
# Define a main() function.
def main():
    checknginx()
      
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

