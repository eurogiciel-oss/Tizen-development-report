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
DIRSRC=./src_DIR
DIRDST=./dst_DIR


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
    *-dir-src)
      DIRSRC=$2
      shift
      shift
    ;;
    *-dir-dst)
      DIRDST=$2
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

#TODO Change to clean help
if [ ${SHOW_HELP} != "no" ]; then
    exit 0
fi


#TO DO
#if [ DIRSRC == "" ]; then
#exit 1
#echo blabla
#fi

#TO DO
#if [ DIRDST == "" ]; then
#exit 1
#echo blabla
#fi


#TOTDO ???
DIRSRC=$(readlink -m ${DIRSRC})
DIRDST=$(readlink -m ${DIRDST})

mkdir -p ${DIRDST}

for rpm_src_file in $(ls ${DIRSRC}/*.src.rpm) ; do
    mkdir -p ${DIRDST}/$(basename ${rpm_src_file})
    cd ${DIRDST}/$(basename ${rpm_src_file})
    rpm2cpio ${rpm_src_file} | cpio -id 
    cd -
done