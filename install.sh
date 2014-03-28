#!/bin/bash

#
# Copyright (c) 2014 Kévin THIERRY <kevin.thierry@open.eurogiciel.org>
#
# See the file LICENSE for copying permission.
#

if [ "$#" -ne 2 ]
then
    echo
    echo "Copy the scripts in the given directory"
    echo
    echo "Usage: \"./install.sh <dest_bin_dir> <dest_data_dir>\""
    echo
    exit 0
fi

BINDIR=$1
DATADIR=$2

# General
install -d $DATADIR/tizen-info/templates
install bin/* $BINDIR
install templates/* $DATADIR/tizen-info/templates

# Multi-user
install -d $DATADIR/tizen-info/multi-user/templates
install -d $DATADIR/tizen-info/multi-user/data/
install multi-user/bin/* $BINDIR
install multi-user/templates/* $DATADIR/tizen-info/multi-user/templates
install multi-user/data/* $DATADIR/tizen-info/multi-user/data

# Gerrit
install -d $DATADIR/tizen-info/gerrit/templates
install gerrit/bin/* $BINDIR
install gerrit/templates/* $DATADIR/tizen-info/gerrit/templates

# Manifest
install -d $DATADIR/tizen-info/manifest/templates
install manifest/bin/* $BINDIR
install manifest/templates/* $DATADIR/tizen-info/manifest/templates

exit 0
