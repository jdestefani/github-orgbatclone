import requests
import sys
from optparse import OptionParser
from subprocess import call


if __name__ == "__main__":
   # Commandline option parsing using optparse
   parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
   parser.add_option("-a", "--assignment_name",
                      action="store",
                      dest="assignment_name",
                      default="",
                      help="Specify the assignment name on Github Classroom")
   parser.add_option("-o", "--organisation",
                      action="store", 
                      dest="organisation_name",
                      default="",
                      help="Specify the organization name on Github")
   (options, args) = parser.parse_args()

   # Force user to input both assignment and organisation name
   if not(options.assignment_name) or not(options.organisation_name):
      parser.error("Both organisation and assignment are mandatory parameters")

   print('[INFO] Organization:' + options.organisation_name + ' - Assignment:' + options.assignment_name)

   # Make HTTP request for JSON list of repositories
   repo_list_request = requests.get('https://api.github.com/orgs/'+options.organisation_name+'/repos?per_page=200')

   # Filter repositories according to assignment name and clone them
   for repository in repo_list_request.json():
       if repository["name"].find(options.assignment_name):
           call(["git", "clone", repository["clone_url"]])
           


