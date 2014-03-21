#!/bin/bash

if [ "$#" -ne 1 ]
then
    echo
    echo "Copy the scripts in the given directory"
    echo
    echo "Usage: \"./install.sh <destination>\""
    echo
    exit -1
fi

BINDIR=$1

# Gerrit elated scripts (Gerrit querries)
install scripts/gerrit/* $BINDIR

# Git repo related scripts
install scripts/repo/* $BINDIR

# Global scripts
install scripts/global/* $BINDIR

exit 0
