#!/bin/bash 


find $1/tmp/deploy/rpm/ -name \*.rpm -exec rpm -qp {} --queryformat='%{SourceRPM}\n' \;| sort | uniq
