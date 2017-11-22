# github-orgbatclone
Python script to perform the batch clone of all the repositories related to a certain assignment in Github Classroom, from a given Github organization, eventually with a specific authentication, rolling back to a specified date.

# How to use it
Without ssh:
```
python batchDownloadScript.py -o organisation_name -a assignment_name -d "YYYY-MM-DD HH:HH" -u username 
```

With ssh:
```
python batchDownloadScript.py -o organisation_name -a assignment_name -d "YYYY-MM-DD HH:HH" -u username -s
```

Note:
* ```organization_name``` is the only mandatory parameter, all the others are optionals.
* Without specifying username, it would not be possible to access private repositories.
* Without assignment name, all the accessible repositories belonging to the organisation will be cloned.
* Without date, the repositories are cloned at the last available commit.
* If present, date must be supplied between quotes and with the specified format

# Modules dependencies
* Subprocess
* Requests (>= 2.8.14)
* Git
* Optparse
* Getpass



