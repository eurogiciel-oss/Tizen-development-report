Tizen-development-report
========================

# Overview

Tizen-development-report provides a bunch of scripts that generate reports regarding the state of Tizen bugs and reviews.

You are more than welcome to report any bugs you find or supply fixes or improvements.

# Dependency

Scripts get-status and get-gerrit-status-open need the json parser jq (http://stedolan.github.io/jq/)

# Requirements

Besides jq you need 2 things to get all the scripts working:

* An access to Tizen Gerrit
* A local, updated copy of the Tizen repos

Note that scripts located in ./scripts/gerrit only require a Gerrit access and that scripts in ./scripts/repo only require a local repo. Scripts in ./scripts/main either require both a Gerrit access and a local repo or a result file.

# Install

	./install <destination>

There isn't an uninstall script (yet).

# Main scripts

##get-status-loop

Return a full report given a list of projects and bug ID. Return results with a csv format.

Usage:

	get-status-loop <path_to_local_repo> <input_file> <invalid_bugs_list>

* "input_file" is a text file containing the bug ID and the corresponding project

* "invalid_bugs_list" is a list of invalid bugs, it is made to refer to the bugs closed as invalid in Jira (or any bugs that are closed without a fix)

You can easily get a bug list from Jira using the export function after a search.

Note that this script was made for the multi-user architecture so it may not suit every usage but the script being fairly simple, it is easy to adapt to your needs.

##get-gerrit-status-open

Generates a status of the opened Gerrit reviews which didn't receive any activity in the last N days. Return results with a csv format.

	get-gerrit-status-open <age_in_days>

##get-status-stats

Returns statistics regarding status, checking a list of status against a generated report file. Return results with a csv format.

Usage:

	get-status <input_file> <status_list>

# Internal scripts

Those scripts are used by the main scripts but can also be run on their own.

##get-invalid
Returns the list of commits that need to be reworked. Only returns the commits that are older than the number of days given as parameter.

##get-to-merge
Returns the list of commits which are ready to be merged. Only returns the commits that are older than the number of days given as parameter.

##get-to-review
Returns the list of commits that need to be reviewed. Only returns the commits that are older than the number of days given as parameter.

##get-to-review-and-verify
Returns the list of commits that need to be reviewed and verified. Only returns the commits that are older than the number of days given as parameter.

##get-to-verify
Returns the list of commits that need to be verified. Only returns the commits that are older than the number of days given as parameter.

##get-status
Return the status of a single bug

##get-gerrit-info
Return the result of a per project query to Gerrit filtered with a regexp.

##get-commit
Return the commit associated with a changeID

##get-repo-status
Return the status of a merged commit; status are MERGED, SUBMITTED, ACCEPTED.

# TO DO

* Allow usage of alternate json parsers (underscore-cli https://github.com/ddopson/underscore-cli)
* Add a script that return stats from a csv file
* Add more fields in the csv file (gerrit-owner...)
* Add an uninstall script
* get-gerrit-status-open fails to parse https://review.tizen.org/gerrit/#/c/16751/
* Improve documentation

# License

Those scripts are licensed under The MIT License (MIT)

http://mit-license.org/
