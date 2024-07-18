#!/bin/bash
# share/tools/pin-python-versions-for-release.sh: Tool to pin python module
# dependencies before ElasticBLAST releases
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Wed 10 Aug 2022 06:01:40 PM EDT
set -ex
TMP=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
trap " /bin/rm -fr $TMP " INT QUIT EXIT HUP KILL ALRM

pin_dependency_versions() {
    fname=$1
    truncate -s 0 $TMP
    pip freeze -r $fname > $TMP
    n=`egrep -n '^##' $TMP | awk -F: '{print $1}'`
    head -n $(($n-1)) $TMP >| $fname
}

if ! python3 -c 'import sys; sys.exit(sys.prefix == sys.base_prefix)' ; then
    echo "ERROR: this script is not running in a virtual environment"
    echo "Please run 'rm -fr .env && make .env' before running this script again"
fi

pin_dependency_versions requirements/base.txt
pin_dependency_versions requirements/test.txt
