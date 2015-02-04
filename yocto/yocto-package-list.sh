#!/bin/bash

WORK_COMMON="/home/kthierry/tizen-distro/build-common/tmp-glibc/work"
WORK_IVI="/home/kthierry/tizen-distro/build-ivi/tmp-glibc/work"
META_TIZEN="/home/kthierry/yocto/meta-tizen"
OE_CORE="/home/kthierry/tizen-distro/meta"
META_OE="/home/kthierry/tizen-distro/meta-openembedded"
REPO="/home/kthierry/jumbo/review.tizen.org/platform/upstream"
LOG="/tmp/yocto-package-list.log"

# Return the greatest version amongst the ones given in parameter
function greater_version() {
    local versions="$1"
    local greater_ver=""
    for ver in $versions; do
        # This needs to be improved:
        if [ "$ver" \> "$greater_ver" ]; then
            greater_ver=$ver
        fi
    done
    if [ "$greater_ver" = "" ]; then
        greater_ver="-"
    fi
    echo "$greater_ver"
}

# List packages and the version used in Tizen-Yocto
function tizen_yocto_packages() {
    local WORK="$1"
    for dir in `ls $WORK`; do
        for pkg in `ls $WORK/$dir`; do
            if [[ $pkg != packagegroup* ]]; then
                local ver=`ls $WORK/$dir/$pkg | sed 's/-r[0-9]*\.*[0-9]*$//'`
                ver=$(greater_version $(echo $ver))
                echo "$pkg,$ver"
            fi
        done
    done
}

# Convert yocto package names to Tizen package names
function convert_pkg_to_tizen() {
    case "$1" in
    "bluez5") echo "bluez";;
    "bjam") echo "boost-jam";;
    "libsoup-2.4") echo "libsoup";;
    "db") echo "db4";;
    "gcc"|"gcc-cross-initial-x86_64"|"gcc-cross-x86_64"|"gcc-runtime"|"libgcc"|"libgcc-initial") echo "gcc49";;
    "glibc-initial"|"glibc-locale") echo "glibc";;
    "gstreamer1.0") echo "gstreamer";;
    gstreamer1.0-*) echo "$1" | sed 's/gstreamer1.0-/gst-/';;
    "sqlite3") echo "sqlite";;
    "gconf") echo "gconf-dbus";;
    "linux-yocto") echo "kernel-common";;
    "libnl") echo "libnl3";;
    "libxml2") echo "$1";;
    libx*) echo "$1" | tr '[:lower:]' '[:upper:]';;
    "libpcre") echo "pcre";;
    "libnss-mdns") echo "nss-mdns";;
    *) echo "$1";;
    esac
}

# Convert Tizen package names to Tizen spec file names
function convert_spec() {
    case "$1" in
    *) echo "$1";;
    esac
}

# Convert Tizen package names to Yocto package names
function convert_pkg_to_yocto() {
    case "$1" in
    "dbus-python")  echo "python-dbus";;
    "gconf-dbus")   echo "gconf";;
    *)              echo "$1";;
    esac
}


# Find the version in Tizen for a given package
function tizen_version() {
    local pkg=`convert_pkg_to_tizen $1`
    local spec=`convert_spec $pkg`

    #local tmpfile=$(mktemp)
    #trap "rm -f $tmpfile" STOP INT QUIT EXIT
    spec="$REPO/$pkg/packaging/$spec.spec"
    
    if [ -e "$spec" ]; then
        #rpmspec --parse $spec > $tmpfile && spec=$tmpfile
        echo $(grep -i "Version:" $spec 2> $LOG | awk '{print $2;}' | head -n 1)
    else
        echo "-"
    fi
}

# Find in what layers the recipe of a package is located
function find_layers() {
    local pkg="$1"
    local pkg_yocto=`convert_pkg_to_yocto $pkg`
    local meta_tizen=$(find $META_TIZEN -name "$pkg\_*.bb" -exec basename {} \; 2> /dev/null | cut -f 2 -d '_' | sed 's/.bb//g')
    if [ "$meta_tizen" != "" ]; then
        local src="Tizen"
    else
        local src="Yocto"
    fi
    local oe_core=$(find $OE_CORE -name "$pkg_yocto\_*.bb" -exec basename {} \; 2> /dev/null | cut -f 2 -d '_' | sed 's/.bb//g')
    local meta_oe=$(find $META_OE -name "$pkg_yocto\_*.bb" -exec basename {} \; 2> /dev/null | cut -f 2 -d '_' | sed 's/.bb//g')
    meta_tizen=`echo $meta_tizen | sed 's! !/!g'`
    oe_core=`echo $oe_core | sed 's! !/!g'`
    meta_oe=`echo $meta_oe | sed 's! !/!g'`
    echo "$src,$meta_tizen,$oe_core,$meta_oe"
}

# Return the older source when given two package versions
function older() {
    local ver_yocto=$1
    local ver_tizen=$2
    if [[ "$ver_tizen" = "-" || "$ver_yocto" = "-" || "$ver_yocto" = "$ver_tizen" ]]; then
        echo "-"
    # This needs to be improved:
    elif [ "$ver_yocto" \< "$ver_tizen" ]; then
        echo "Yocto"
    else
        echo "Tizen"
    fi
}

# Return the greatest version amongst the ones in Yocto layers
function greater_version_yocto() {
    local oe_core=`echo $1 | cut -f 3 -d ','`
    local meta_oe=`echo $1 | cut -f 4 -d ','`
    local versions=`echo "$oe_core $meta_oe" | sed 's!/! !g'`
    greater_version $versions
}

echo "Package,Tizen-Yocto version,Tizen version,Older / To update,Source,In meta-tizen,In oe-core,In meta-oe"

res=$(echo "$(tizen_yocto_packages $WORK_COMMON) $(tizen_yocto_packages $WORK_IVI)" | sed 's/-native,/,/g' | tr ' ' '\n' | sort -u)

for pkg_ver in $res; do
    pkg=`echo $pkg_ver | cut -f 1 -d ','`
    layers=`find_layers $pkg`
    ver_yocto=`greater_version_yocto $layers`
    ver_tizen=`tizen_version $pkg`
    to_update=`older $ver_yocto $ver_tizen`
    echo "$pkg_ver,$ver_tizen,$to_update,$layers"
done
