Tizen-development-report
========================

# Overview

Tizen-development-report provides a bunch of scripts that generate a csv file containing the state of a given list of bugs.

Note that those scripts have originaly been made to generate a report regarding the state of the multi-user related bugs so it might not suit every usages. However you are free to clone this project and make any changes you want.

If you find any bugs or want to supply a fix/improvement, you are welcome !

# Dependency

The script get-status needs the json parser jq (http://stedolan.github.io/jq/)

Other json parsers can be used. In this case you need to adapt the script "get-status".

# Requirements

You need 2 things to get the scripts working:

* An access to Tizen Gerrit 
* A local, updated copy of the Tizen repos

# Install

	./install <destination>

# Run

The script that you need to run to get a full report given a list of projects and bug ID is "get-status-loop"

Usage:

	get-status-loop <path_to_local_repo> <input_file> <invalid_bugs_list>

* "input_file" is a text file containing the bug ID and the corresponding project

* "invalid_bugs_list" is a list of invalid bugs, it is made to refer to the bugs closed as invalid in Jira (or any bugs that are closed without a fix)

# Mechanism

* Check the bug ID against a list of invalid bugs
* Query GErrit to get a status
* If the status is "MERGED", check against the local repo whether it is submitted and accepted or not.

# Internal scripts

Those scripts are used by the main script "get-status-loop" but can also be run on their own.

* get-status
Return the status of a single bug

* get-gerrit-info
Return the result of a per project query to Gerrit filtered with a regexp. 

* get-commit
Return the commit associated with a changeID

* get-repo-status
Return the status of a merged commit; status are MERGED, SUBMITTED, ACCEPTED.

# TO DO

* Allow usage of alternate json parsers (underscore-cli https://github.com/ddopson/underscore-cli)
* Add a script that return stats from a csv file
* Add more fields in the csv file (gerrit-owner...)

# License

Those scripts are licensed under The MIT License (MIT)

http://mit-license.org/
