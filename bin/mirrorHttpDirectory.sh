#!/bin/bash
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Intel, Inc.
# License: GPLv2
# Authors: Ronan Le Martret <ronan.lemartret@open.eurogiciel.org>
# Authors: Kevin Thierry <kevin.thierry@open.eurogiciel.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
#Created on  13 oct. 2014
#
#@author: ronan.lemartret@open.eurogiciel.org
#

SHOW_HELP="no"
URL=""
DIR=./default_mirror_directory


if [ "$#" -eq 0 ]
then
 SHOW_HELP="yes"
fi

while test $# -gt 0; do
  case $1 in
    *-help)
      SHOW_HELP="yes"
      shift
    ;;
    *-h)
      SHOW_HELP="yes"
      shift
    ;;
    *-dir)
      DIR=$2
      shift
      shift
    ;;
    *-url)
      URL=$2
      shift
      shift
    ;;
    *)
      echo "Unknown parameter $1."
      echo "This script is not accepting this parameter currently."
      exit 1
    ;;
  esac
done

#TO DO
#if [ URL == "" ]; then
#exit 1
#echo blabla
#fi

#TODO Change to clean help
if [ ${SHOW_HELP} != "no" ]; then
    echo "Usage: $0 --dir <local dir containingmirror default=./default_mirror_directory
> --url <url containing mirror>"
    echo ""
    echo "If option --url is used, log files are download to local  dir."
    echo ""
    echo "Example: $0 --url http://download.tizen.org/snapshots/tizen/common/latest/repos/x86_64-wayland/source/"
    echo "Example: $0 --dir ./default_mirror_directory
 --url http://download.tizen.org/snapshots/tizen/common/latest/repos/x86_64-wayland/source/"
    exit 0
fi

#WARNING TO DO --cut-dirs=9 is not clean use cut/count/wc or wathever to do that clean
if [ ! -z ${URL} ]
then
    mkdir -p ${DIR}
    #TODO is it good ?
    wget --directory-prefix=${DIR} --reject index.html* --mirror --no-parent --no-host-directories --cut-dirs=9 ${URL}
fi


