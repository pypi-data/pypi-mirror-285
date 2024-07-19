#!/bin/bash
# pd-scalability-tests.sh: Executes various makefile targets to test how many
# k8s nodes can attached to a persistent disk. Note: this script is intended to
# strictly tests the ability to attach many nodes to a persistent disk and start
# BLAST searches (not necessarily run them to completion or optimally).
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Mon 16 Mar 2020 07:06:26 AM EST

set -xeuo pipefail
shopt -s nullglob

SCRIPT_DIR=$(cd "`dirname "$0"`"; pwd)

source $SCRIPT_DIR/../config/setenv-nr.sh
export ELB_QUERIES=gs://elastic-blast-samples/queries/protein/dark-matter-500000.faa.gz
export ELB_BLAST_OPTIONS='-threshold 100 -word_size 6 -comp_based_stats 0 -evalue 1.0e-50 -max_target_seqs 10'

export ELB_USE_PREEMPTIBLE=1
# Adjust accordingly. Run long enough to load the cluster fully.
export ELB_JOB_TIMEOUT=${1:-"25m"}

#export ELB_BATCH_LEN=10000

cleanup_resources_on_error() {
    set +e
    time make delete
    exit 1;
}

trap "cleanup_resources_on_error;" INT QUIT HUP KILL ALRM ERR

number_of_nodes_in_cluster=(20 40 80)
number_of_nodes_in_cluster=(80 160 320 640)
# 124 nodes is currently (3/17/2020) close to the limit of vCPUs for this project/region
number_of_nodes_in_cluster=(124 320 640)

time make split
NUM_SPLITS=$(find split/jobs -type f -name "batch*.yaml" | wc -l)
if [[ $NUM_SPLITS -lt ${number_of_nodes_in_cluster[-1]} ]] ; then
    echo "Error: please reduce ELB_BATCH_LEN so that all nodes in the cluster can be used"
    exit 1
fi
if [[ $NUM_SPLITS -gt 5000 ]] ; then
    echo "Error: please increase ELB_BATCH_LEN so that less than 5,000 k8s jobs are created (this is a current GKE limit)"
    exit 1
fi

time make setup_pd

for n in ${number_of_nodes_in_cluster[@]}; do
    echo "Testing with $n hosts";
    export ELB_NUM_NODES=$n
    make show_config   # for debugging
    time make create deploy;
    time timeout $ELB_JOB_TIMEOUT make timed_run || true
    time make test_asn_results download_split_queries 
    time make delete
    time parallel gzip {} ::: *fa
    [ -d $n ] || mkdir $n
    mv batch*out.gz *.fa.gz $n
done

time make clean
