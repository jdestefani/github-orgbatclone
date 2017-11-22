# github-orgbatclone
Python script to perform the batch clone of all the repositories related to a certain assignment in Github Classroom, from a given Github organization, eventually with a specific authentication.

# How to use it
```
python batchDownloadScript.py -o organisation_name -a assignment_name -d "YYYY-MM-DD HH:HH" -u username 
```

Note:
* ```organization_name``` is the only mandatory parameter, all the others are optionals.
* Date must be supplied between quotes and with the specified format


# Dependencies
* Subprocess
* Requests (>= 2.8.14)
* Git




