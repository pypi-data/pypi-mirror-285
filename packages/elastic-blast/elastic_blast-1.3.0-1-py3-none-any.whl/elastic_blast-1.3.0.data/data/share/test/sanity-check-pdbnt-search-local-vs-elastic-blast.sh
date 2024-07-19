#!/bin/bash
# test/sanity-check-pdbnt-search-local-vs-elastic-blast.sh: Downloads the input nd
# results produced by the bare bones test k8s system and compares them with
# running BLAST locally.
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Thu 20 Feb 2020 03:23:54 PM EST

export PATH=/bin:/usr/bin
set -xeuo pipefail

DB=${1:-"pdbnt"}

# Assumes Elastic BLAST input and results exist
rm -f *.fa *.out
gsutil -m cp gs://${USER}-test/*.fa .
gsutil -m cp gs://${USER}-test/*.out .

# Please do NOT abuse the command line below, there are egress charges if not executed at GCP
[ -f ${DB}.nin ] || update_blastdb.pl --source gcp ${DB}
parallel -t blastn -db ./${DB} -query {} -out {.}.ref.out ::: *.fa
for f in batch*.ref.out; do
    t=$(echo $f | sed 's/.ref//')
    diff $f $t
done
echo "Don't forget to delete the locally downloaded pdbnt!"
