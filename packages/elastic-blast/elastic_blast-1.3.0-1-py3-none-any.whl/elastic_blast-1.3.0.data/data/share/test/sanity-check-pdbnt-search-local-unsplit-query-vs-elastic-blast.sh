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
UNSPLIT_QUERY=${2:-"gs://elastic-blast-samples/queries/MANE/MANE.GRCh38.v0.8.select_refseq_rna.fna"}

QUERY=`mktemp -t $(basename -s .sh $0)-XXXXXXX.fsa`
RESULTS=`mktemp -t $(basename -s .sh $0)-XXXXXXX-blastn.out`
EB_RESULTS=`mktemp -t $(basename -s .sh $0)-XXXXXXX-elastic-blast.out`
trap " /bin/rm -fr $QUERY $RESULTS $EB_RESULTS " INT QUIT EXIT HUP KILL ALRM

gsutil -m cp $UNSPLIT_QUERY $QUERY

# Assumes Elastic BLAST input and results exist
rm *.out
gsutil -m cp gs://${USER}-test/*.out .

# Please do NOT abuse the command line below, there are egress charges if not executed at GCP
[ -f ${DB}.nin ] || update_blastdb.pl --source gcp ${DB}

blastn -db ./${DB} -query $QUERY | sort > $RESULTS
cat batch*.out | sort > $EB_RESULTS

ls -lh $EB_RESULTS $RESULTS
wc -l $EB_RESULTS $RESULTS
diff $EB_RESULTS $RESULTS

echo "Don't forget to delete the locally downloaded pdbnt!"
