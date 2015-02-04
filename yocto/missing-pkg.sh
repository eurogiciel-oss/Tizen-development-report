#!/bin/bash

MANIFEST_DIR="$1"
YOCTO_COMMON="$2/tmp-glibc/work"
YOCTO_IVI="$3/tmp-glibc/work"
LAYERS="$4/meta*"
REPO="$5"

TMP=$(mktemp)
TMP2=$(mktemp)
trap "rm -f $TMP $TMP2" STOP INT QUIT EXIT

# Tizen image package list from manifest file
for manifest in $(ls $MANIFEST_DIR); do
    grep -rn project $MANIFEST_DIR/$manifest | cut -f 2 -d '"' >> $TMP
done

cat $TMP | sort -u > $TMP2

# Convert yocto package names to Tizen package names
function convert_pkg_to_yocto() {
    local pkg=`echo $1 | sed 's/_/-/g'`
    case "$pkg" in
    "bluez")                                echo "bluez5";;
    "libsoup")                              echo "libsoup-2.4";;
    "sqlite")                               echo "sqlite3";;
    "kernel-common")                        echo "linux-yocto";;
    "SDL")                                  echo "libsdl";;
    "glib")                                 echo "glib-2.0";;
    "pkg-config")                           echo "pkgconfig";;
    "gtk-doc")                              echo "gtk-doc-stub";;
    "boost-jam")                            echo "bjam-native";;
    "nss-mdns"|"yaml")                      echo "lib${pkg}";;
    "aul-1")                                echo "aul";;
    "gconf-dbus")                           echo "gconf";;
    "llvm")                                 echo "llvm3.3";;
    "gstreamer")                            echo "gstreamer1.0";;
    "dejavu-fonts")                         echo "ttf-dejavu";;
    "libjpeg6")                             echo "jpeg";;
    "db4"|"gcc49"|"libnl3"|"autoconf213")   echo "$pkg" | sed 's/[0-9]//g';;
    "ninja")                                echo "${pkg}-native";;
    "kernel-x86-ivi"|linux-*)               echo "linux-yocto";;
    gst-*)                                  echo "$pkg" | sed 's/gst-/gstreamer1.0-/';;
    libX*|"python-PyYAML"|"libGLU")         echo "$pkg" | tr '[:upper:]' '[:lower:]';;
    *)                                      echo "$pkg";;
    esac
}

# Return domain of a package
function domain() {
    pkg="$1"
    ls $REPO/$pkg/packaging/*.spec &> /dev/null
    if [ $? -eq 0 ]; then
        echo $(grep -i "Group:" $REPO/$pkg/packaging/*.spec | head -n 1 | sed 's/Group: //g')
    else
        echo ""
    fi
}

echo "Package,Domain"

count_missing=0
count_total=0
while read pkg; do
    pkg_name=`basename $pkg`
    count_total=$(($count_total+1))
    pkg_yocto=`convert_pkg_to_yocto $pkg_name`

    in_tizen_yocto=`find $LAYERS -type f -name "${pkg_yocto}_*.bb" | wc -l`
    if [ $in_tizen_yocto -eq "0" ]; then
        count_missing=$(($count_missing+1))
        echo "$pkg,$(domain $pkg)"
    fi
done < $TMP2

echo
echo "Total:$count_total    Available recipes:$(($count_total-$count_missing))    Missing:$count_missing"
