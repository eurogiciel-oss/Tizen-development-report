#!/bin/bash

if [ "$#" -ne 1 ]
then
    echo ""
    echo "Copy the scripts in the given directory"
    echo ""
    echo "Usage: \"./install.sh <destination>\""
    echo ""
    exit -1
fi

BINDIR=$1

install scripts/gerrit/get-gerrit-info $BINDIR
install scripts/global/get-status $BINDIR
install scripts/global/get-status-loop $BINDIR
install scripts/repo/get-commit $BINDIR
install scripts/repo/get-repo-status $BINDIR

exit 0
