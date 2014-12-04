#!/bin/bash

for x in Tizen:3.0.M14.2:IVI Tizen:3.0.M14.3:IVI Tizen:IVI; do
	obsfile=$(echo $x | sed 's/:/_/g').obs
	outfile=$(echo $x | sed 's/:/_/g').csv

	[[ -f $obsfile ]] || $(dirname $0)/extract_obs_infos.sh $x | sort  >$obsfile

	cat <<EOF >$outfile
Project;Execution date
$x;$(date +%Y%m%d.%H%M%S)

Package;Repository;Version;Upstream Tag;First Rev;Last Rev;Eurogiciel Commits;Intel Commits;Total Commits;License
EOF

	$(dirname $0)/extract_git_infos.sh <$obsfile | sort >>$outfile
done

