#!/bin/bash

rm -f reviews-status.tmp reviews-age.tmp

SPREADSHEET="spreadsheets/gerrit-status-$(date --rfc-3339='date').csv"

function get_gerrit_status() {

    local AGE=$1
    local TEMPLATE=$2

    # Changes to merge
    ./tizen-info -q "is:open age:${AGE}d label:Code-Review+2 label:Verified+1 NOT label:Verified-1 NOT label:Code-Review-2" -t $TEMPLATE | sed "s@__GERRIT_ACTION__@TO_MERGE@g"

    # Changes to review
    ./tizen-info -q "status:open age:${AGE}d label:Verified+1 NOT label:Verified-1 NOT label:Code-Review-2 NOT label:Code-Review+2" -t $TEMPLATE | sed "s@__GERRIT_ACTION__@TO_REVIEW@g"

    # Changes to verify
    ./tizen-info -q "status:open age:${AGE}d label:Code-Review+2 NOT label:Verified+1 NOT label:Verified-1 NOT label:Code-Review-2" -t $TEMPLATE | sed "s@__GERRIT_ACTION__@TO_VERIFY@g"

    # Changes to review and verify
    ./tizen-info -q "status:open age:${AGE}d NOT label:Code-Review+2 NOT label:Verified+1 NOT label:Verified-1 NOT label:Code-Review-2" -t $TEMPLATE | sed "s@__GERRIT_ACTION__@TO_REVIEW_AND_VERIFY@g"

    # Invalid changes
    ./tizen-info -q "status:open age:${AGE}d (label:Verified-1 OR label:Code-Review-2)" -t $TEMPLATE | sed "s@__GERRIT_ACTION__@INVALID@g"
}

function reviews_status() {

    local TO_MERGE=
    local TO_REVIEW=
    local TO_VERIFY=
    local TO_REVIEW_AND_VERIFY=
    local INVALID=
    local TOTAL=

    for spreadsheet in `ls spreadsheets`; do
        TO_MERGE="$TO_MERGE $(grep -c TO_MERGE, spreadsheets/$spreadsheet)"
        TO_REVIEW="$TO_REVIEW $(grep -c TO_REVIEW, spreadsheets/$spreadsheet)"
        TO_VERIFY="$TO_VERIFY $(grep -c TO_VERIFY, spreadsheets/$spreadsheet)"
        TO_REVIEW_AND_VERIFY="$TO_REVIEW_AND_VERIFY $(grep -c TO_REVIEW_AND_VERIFY, spreadsheets/$spreadsheet)"
        INVALID="$INVALID $(grep -c INVALID, spreadsheets/$spreadsheet)"
        TOTAL="$TOTAL $(cat spreadsheets/$spreadsheet | wc -l)"
    done

    echo $TO_MERGE
    echo $TO_REVIEW
    echo $TO_VERIFY
    echo $TO_REVIEW_AND_VERIFY
    echo $INVALID
    echo $TOTAL
}

function reviews_age() {

    local TWO=0
    local WEEK=0
    local TWO_WEEKS=0
    local MONTH=0
    local THREE_MONTHS=0
    local TOO_MANY_TIME=0

    while read line
    do
        upload=$(echo ${line} | cut -f 6 -d ',')
        update=$(echo ${line} | cut -f 8 -d ',')

        if [ ${update} -eq 2 ]
        then
            TWO=$((${TWO}+1))
        elif [ ${update} -lt 7 ]
        then
            WEEK=$((${WEEK}+1))
        elif [ ${update} -lt 14 ]
        then
            TWO_WEEKS=$((${TWO_WEEKS}+1))
        elif [ ${update} -lt 30 ]
        then
            MONTH=$((${MONTH}+1))
        elif [ ${update} -lt 90 ]
        then
            THREE_MONTHS=$((${THREE_MONTHS}+1))
        else
            TOO_MANY_TIME=$((${TOO_MANY_TIME}+1))
        fi
    done < $SPREADSHEET

    echo ${TWO} ${WEEK} ${TWO_WEEKS} ${MONTH} ${THREE_MONTHS} ${TOO_MANY_TIME}
}

get_gerrit_status 2 templates/tizen-info-template.csv > $SPREADSHEET
reviews_status > reviews-status.tmp
reviews_age > reviews-age.tmp

python gerrit-status.py fetch
python gerrit-status.py process
