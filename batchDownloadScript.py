import requests
import sys
import os
from optparse import OptionParser
import subprocess
import getpass
import math
import pdb
import csv

REPOSITORIES_PER_PAGE = 100

def gitLogToCSV(directory_name):
   GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message']
   GIT_LOG_FORMAT = ['%H', '%an', '%ae', '%ad', '%s']
   GIT_LOG_FORMAT = '%x1f'.join(GIT_LOG_FORMAT) + '%x1e' # Add ASCII field separator and record separator to simplify parsing

   p = subprocess.Popen('git --git-dir ./%s/.git log --format="%s"' % (directory_name,GIT_LOG_FORMAT), shell=True, stdout=subprocess.PIPE)
   (log, _) = p.communicate()
   log = log.decode('UTF-8') # Decode the output from git log to UTF-8
   log = log.strip('\n\x1e').split("\x1e")
   log = [row.strip().split("\x1f") for row in log]
   log = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in log]

   with open('%s/gitLog.csv' % directory_name,'w') as f:
      w = csv.DictWriter(f,GIT_COMMIT_FIELDS)
      w.writerow(dict((index,index) for index in GIT_COMMIT_FIELDS))
      w.writerows(log)


if __name__ == "__main__":
   # Commandline option parsing using optparse
   parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
   parser.add_option("-a", "--assignment_name",
                      action="store",
                      dest="assignment_name",
                      default="",
                      help="Specify the assignment name on Github Classroom")
   parser.add_option("-d", "--checkout_date",
                      action="store",
                      dest="checkout_date",
                      default="",
                      help='Specify the checkout date (format "YYYY-MM-DD HH:MM") to which the Git repositories should be moved')
   parser.add_option("-o", "--organisation",
                      action="store", 
                      dest="organisation_name",
                      default="",
                      help="Specify the organization name on Github")
   parser.add_option("-u", "--username",
                      action="store", 
                      dest="username",
                      default="",
                      help="Specify the username on Github")
   parser.add_option("-s", "--ssh",
                      action="store_true",
                      dest="ssh_flag",
                      default=False,
                      help="Use ssh instead of default https connection to clone")
   (options, args) = parser.parse_args()

   # Force user to input both assignment and organisation name
   if not(options.organisation_name):
      parser.error("Organisation name is a mandatory parameter")

   list_requests = []

   print('[INFO] Organization: ' + options.organisation_name)
   print('[INFO] Using ssh connection: ' + str(options.ssh_flag))

   # If an assignment name is passed, print it
   if options.assignment_name:
      print('[INFO] Assignment: ' + options.assignment_name)

   # If a username is passed, require authentication
   if options.username:
      print('Insert password for Github authentication for ' + options.username + ':')
      password = getpass.getpass()

      # Make a request to get the number of repositories and compute the number of pages to request
      org_request =requests.get('https://api.github.com/orgs/'+options.organisation_name,auth=(options.username,password))
      repositories = org_request.json()["total_private_repos"] 
      pages = int(math.ceil(repositories/float(REPOSITORIES_PER_PAGE)))

      # Make HTTP requests for JSON list of repositories with credentials
      for i in range(pages):
         list_requests.append(requests.get('https://api.github.com/orgs/'+options.organisation_name+'/repos?per_page=100&page='+str(i+1),auth=(options.username,password)))
   else:
      # Make a request to get the number of repositories and compute the number of pages to request
      org_request = requests.get('https://api.github.com/orgs/'+options.organisation_name)
      repositories = org_request.json()["public_repos"]
      pages = int(math.ceil(repositories/float(REPOSITORIES_PER_PAGE)))

      for i in range(pages):
         # Make HTTP request for JSON list of repositories without credentials
         list_requests.append(requests.get('https://api.github.com/orgs/'+options.organisation_name+'/repos?per_page=100&page='+str(i+1)))

   count = 0
   for repo_list_request in list_requests:
      
      #Download repositories if correct request
      if repo_list_request.status_code == requests.codes.ok:
         curr_dir = os.getcwd()
         # Filter repositories according to assignment name (if present) and clone them
         for repository in repo_list_request.json():
            clone_repository = False
            # If an assignment name is provided, check out only the repositories with that name
            if options.assignment_name:
               if repository["name"].find(options.assignment_name) != -1:
                  clone_repository = True
            else: # Otherwise check out all the repositories
               clone_repository = True

            if clone_repository: # If the repository should be cloned
               print('[INFO] Cloning repository ' + repository["name"])
               count = count + 1
               if options.ssh_flag: # Select download mode according to flag
                  subprocess.call(["git", "clone", repository["ssh_url"]])
               else:
                  subprocess.call(["git", "clone", repository["clone_url"]])
               gitLogToCSV(repository["name"]) #Before rolling back the repository, generate the CSV file of the logs
               # If a checkout date is set and the clone operation suceeded
               if options.checkout_date and os.path.exists(os.path.join(curr_dir,repository["name"])):
                  os.chdir(os.path.join(curr_dir,repository["name"])) # cd into the repository
                  commit_hash = subprocess.check_output(['git','rev-list', '-n', '1', '--before="'+options.checkout_date+'"', 'master']) # Find commit hash before desired dates
                  subprocess.call(['git','checkout', '-b', 'deadline', commit_hash[:-1].decode("UTF-8")]) # Create and checkout to a deadline branch given commit hash
                  os.chdir(curr_dir) #cd out of the repository

      else:# Raise execption otherwise
         repo_list_request.raise_for_status()

   print("[INFO] Total count: %d" % count)         







