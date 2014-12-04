#!/bin/bash 

PARALLEL_JOBS=16

PROJECT=${1:-Tizen:Common}
SRV=https://api.tizen.org
#SRV=https://obs.vannes

function parallel_jobs {
	local max_number=$((0 + ${1:-0}))
	while true; do
		jobs &>/dev/null
		if [[ $(jobs -p | wc -l) -lt $max_number ]]; then
			break
		fi
		sleep 0.3
	done
}

function get_pkg_infos() {
	local srv=$1
	local project=$2
	local pkgname=$3

	local tmpfile=$(mktemp)
	trap "rm -f ${tmpfile}*" STOP INT QUIT EXIT

	osc -A $srv list -e $project $pkgname >$tmpfile 2>/dev/null
	[[ $? -ne 0 ]] && return 1

	specname=$(egrep ":${pkgname}\.spec$" $tmpfile 2>/dev/null)
	[[ -z "$specname" ]] && specname=$(egrep "\.spec$" $tmpfile | head -1)

	# find spec file name
	osc -A $srv cat $project $pkgname $specname >$tmpfile 2>/dev/null

	specfile=$tmpfile
	rpmspec --parse $specfile >${tmpfile}.spec 2>/dev/null && specfile=${tmpfile}.spec

	repo=$(grep VCS: $specfile | awk '{print $2;}' | cut -f1 -d'#')
	rev=$(grep VCS: $specfile | awk '{print $2;}' | cut -f2 -d'#')
	upstreamversion=$(grep -i "Version:" $specfile| awk '{print $2;}' | head -n 1)
	license=$(grep License: $specfile | sed 's/License:[ \t]*//g' | awk '{printf("%s/",$0);}' | sed 's|/$||g' | tr ';' ' ')

	echo "$pkgname;$repo;$rev;$upstreamversion;$license"
	echo "OBS: $pkgname $repo $upstreamversion $rev" >&2

	return 0
}

for pkg in $(osc -A $SRV ls $PROJECT); do
	parallel_jobs $PARALLEL_JOBS
	get_pkg_infos $SRV $PROJECT $pkg &
done

parallel_jobs 1
