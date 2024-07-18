#!/bin/bash
# share/tools/loc.sh: Script to count number of lines of code per ElasticBLAST release
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Fri Sep 25 11:38:09 2020

set -euo pipefail
shopt -s nullglob

which cloc >& /dev/null || { echo "Missing cloc dependency"; exit 1; }

for v in $(git tag | sort -Vr); do 
    echo "******* ElasticBLAST version $v *********"
    cloc --git $v
done
