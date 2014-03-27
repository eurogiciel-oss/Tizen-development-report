Tizen-development-report
========================

# Overview

Tizen-development-report provides a bunch of scripts that generate reports regarding the state of Tizen bugs and reviews.

You are more than welcome to report any bugs you find or supply fixes or improvements.

# Dependency

The main script, tizen-info relies on the json parser jq (http://stedolan.github.io/jq/).

# Requirements

Besides jq you need 2 things to get all the scripts working:

* An access to Tizen Gerrit
* A local, updated copy of the Tizen repos containing all projects' git repo.

# Install

	./install <binary_destination> <data_destination>

There isn't an uninstall script (yet).

# Main script

## tizen-info

Return a full report whose results match the given parameters.

Full documentation:

	tizen-info -h

# Other scripts

## Multi-user

tizen-info-multiuser

Generates a status of the multi-user related issues.

## Gerrit

Generates a status of the pending reviews in Gerrit.

# Old scripts

Old scripts can be found on the branch v1_2014-03-25.

# TO DO

* Allow usage of alternate json parsers (underscore-cli https://github.com/ddopson/underscore-cli)
* Return more data (gerrit-owner...)
* Add an uninstall script
* Improve documentation

# License

Those scripts are licensed under The MIT License (MIT)

http://mit-license.org/
