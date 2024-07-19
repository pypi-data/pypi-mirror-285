#!/bin/bash

# FIXME: If this script is to run in TeamCity, consider using bash functions to report status/time/information
# See: https://gist.github.com/VladRassokhin/e24509b7a85386e6374b7580c840dc71

# FIXME: IMHO this script should be modularized to reuse existing automated tests, e.g.:
# Test-blast-search produces BLAST results, then this script picks them up,
# runs the equivalent BLAST+ search and produces a report indicating success, failure, and/or performance degradation
# For a simple, one-off example, please see
# sanity-check-pdbnt-search-local-unsplit-query-vs-elastic-blast.sh in this
# directory

print_help() {
    echo "##############################################################################################"
    echo "#                               Elastic BLAST regression test suite v 0.1                    #"
    echo "##############################################################################################"
    echo " This script runs ElasticBLAST against the specified BLASTDB and selected queries from that  "
    echo " database and compares the results against those produced by BLAST+ run locally in           "
    echo " multi-threaded mode with 16 threads."
    echo "usage: $0 \"blastdb\" [ query_file ]"
    echo "       blastdb - a BLAST DB to run tests on.   Default: pdbnt"
    echo "       query_file   - nucleotide fasta query file. optional"
    echo "                      default: will bre created from given databases"
    echo "##############################################################################################"
    echo "#                    BLAST DB available for usage and testing on GCP                         #"
    echo "##############################################################################################"
    update_blastdb.pl --showall --source gcp | grep -v Connected | sort | awk '{ printf("%3d        %s\n", NR,$0);}'
    echo "#################################################################################"
    echo "DONE."
    exit 0
}

if [ "X$1" = "X-h"  ] ; then
	print_help
fi

if [ "X$1" = "X-help"  ] ; then
	print_help
fi

# ........................................................................
TEST_DB_LIST=${1:-"pdbnt"}
TEST_QUERIES=${2:-"create"}
export ELB_JOB_TIMEOUT=15m

tm0=`date +%s`
tm00=$tm0

echo "TEST_DB_LIST: $TEST_DB_LIST"
if [ "$TEST_QUERIES" = "create" ] ; then
	echo "TEST_QUERIES: will be created from provided BLAST DB list"
else
	echo "TEST_QUERIES: $TEST_QUERIES"
fi
# retrieve local pdbnt copy from GCP

if [ -d "./LOCAL_BLASTDB" ] ; then
	rm -rf ./LOCAL_BLASTDB 2>&1   1>/dev/null
fi	
mkdir "./LOCAL_BLASTDB"
if [ ! -d  "./LOCAL_BLASTDB" ] ; then
          echo "ERROR: can't create ./LOCAL_BLASTDB"
fi
echo "INFO:  created ./LOCAL_BLASTDB"
export BLASTDB=`pwd`/LOCAL_BLASTDB

tm0=`date +%s`
pushd ./LOCAL_BLASTDB 
for ONE_DB in $TEST_DB_LIST 
do
#echo "DEBUG: update_blastdb.pl $ONE_DB --source gcp  "
	update_blastdb.pl $ONE_DB --source gcp  
	echo "INFO: copied $ONE_DB  from GCP "
#	ls -l .
done   
popd
tm1=`date +%s`
tm_elapsed=`expr $tm1 - $tm0`

echo "INFO: copied $TEST_DB_LIST from GCP. elapsed $tm_elapsed sec "

# ATT: don't calculate minimal PD size, will be done automaticallu in Makefile


# STEP: CREATE TEST QUERIES IF NEEDED
if [ "$TEST_QUERIES" = "create" ] ; then
	# CREATE DIRECTORY FOR TEST QUERIES
	if [ -d ./test_queries ] ; then
		rm -rf ./test_queries
	fi
	mkdir ./test_queries
	if [ ! -d ./test_queries ] ; then
		echo "ERROR: can't create ./test_queries"
		exit 1
	fi
	echo "INFO:  created ./test_queries"

	# dump  1200 lines from each db provided
	TEST_NUM=0
	OUT_TEST_NAME="./test_queries/test_all.fna"
	touch $OUT_TEST_NAME
	for ONE_DB in $TEST_DB_LIST 
	do
		TEST_NUM=`expr $TEST_NUM + 1`
		blastdbcmd  -dbtype nucl -db $ONE_DB  -entry all | grep -v "NNNNNNNNNNNNNN" | head -12000 >> $OUT_TEST_NAME
		if [ ! -e "$OUT_TEST_NAME"  ] ; then
			echo "ERROR: can't  dump $ONE_DB to $OUT_TEST_NAME "
			exit 1
		fi
		echo "" >> $OUT_TEST_NAME
	done
	echo "INFO: created $TEST_NUM file with test queries"
	TEST_QUERIES="${OUT_TEST_NAME}"
fi	
#echo "INFO: TEST_DB_LIST: $TEST_DB_LIST"
#echo "INFO: TEST_QUERIES: $TEST_QUERIES"

# STEP: SPLIT TEST QUERIES:
# gs://elastic-blast-samples/queries/tests/
TEST_Q_BN=`basename $TEST_QUERIES`
gsutil -q stat "gs://elastic-blast-samples/queries/tests/${TEST_Q_BN}"
stat_ret="$?"
if [ $stat_ret -eq  0 ] ; then
	# delete old object
	gsutil -q rm "gs://elastic-blast-samples/queries/tests/${TEST_Q_BN}"
fi
#echo gsutil -q cp $TEST_QUERIES "gs://elastic-blast-samples/queries/tests/${TEST_Q_BN}" 
gsutil -q cp $TEST_QUERIES "gs://elastic-blast-samples/queries/tests/${TEST_Q_BN}" 
gsutil -q stat "gs://elastic-blast-samples/queries/tests/${TEST_Q_BN}"
stat_ret="$?"
if [ $stat_ret -ne  0  ] ; then
	echo "ERROR: can't upload test queries to gs://elastic-blast-samples/queries/tests/${TEST_Q_BN}"
	exit 1
fi	

echo "INFO: test queries uploaded to the gs://elastic-blast-samples/queries/tests/${TEST_Q_BN}"

# STEP:  run tests on CLUSTER
export ELB_GCP_PROJECT=ncbi-sandbox-blast
export ELB_GCP_REGION=us-east4
export ELB_GCP_ZONE=us-east4-b
export ELB_QUERIES="gs://elastic-blast-samples/queries/tests/${TEST_Q_BN}"
export DOWNLOADED_RESULTS="./gcp_results"
export DOWNLOADED_QUERY_BATCHES="./batches"
export ELB_DB="$TEST_DB_LIST"
export ELB_OUTFMT=6
export ELB_USE_PREEMPTIBLE=1


echo "INFO: ============================================================="
echo "INFO: =        THIS PARAMETERS WILL BE USED IN Makefile           ="
echo "INFO: ============================================================="
echo "INFO: ELB_QUERIES:                  $ELB_QUERIES"
echo "INFO: ELB_DB:                       $ELB_DB"
echo "INFO: DOWNLOADED_RESULTS:           $DOWNLOADED_RESULTS"
echo "INFO: DOWNLOADED_QUERY_BATCHES:     $DOWNLOADED_QUERY_BATCHES"
echo "INFO: ELB_OUTFMT:                   $ELB_OUTFMT"
echo "INFO: ELB_USE_PREEMPTIBLE:          $ELB_USE_PREEMPTIBLE"
echo "INFO: ============================================================="

if [ "X${ELB_TEST_MODE}" != "XLOCAL" ] ; then
# STEP: START CLUSTER, PREPARE PD, QUERIES
tm0=`date +%s`
tm00=$tm0
echo "INFO: START CLUSTER NORMAL WAY VIA MAKEFILE..."
make -C .. all 
if [ $? -ne 0 ] ; then
	MAKE_ERROR_CODE="$?"
	echo "ERROR: 'make all' failed: MAKE_ERROR_COD: E${MAKE_ERROR_CODE}" 
	make -C .. delete
	exit 1
fi	
tm1=`date +%s`
tm_elapsed=`expr $tm1 - $tm0`
echo "INFO: CLUSTER READY. ELAPSED: $tm_elapsed SEC"

echo "INFO: START JOBS..."
tm0=`date +%s`
make -C .. timed_run test_summary
if [ $? -ne 0 ] ; then
	MAKE_ERROR_CODE="$?"
	echo "ERROR: 'make timed_run' failed: MAKE_ERROR_COD: E${MAKE_ERROR_CODE}" 
	make -C .. delete
	exit 1
fi	
tm1=`date +%s`
tm_elapsed=`expr $tm1 - $tm0`
echo "INFO: JOBS ARE FINISHED: ELAPSED: $tm_elapsed SEC"
else
	echo "INFO: BYPASS GCP PART, RUN LOCAL TEST ONLY"
fi


echo "INFO: GET RESULTS AND BATCHES"
tm0=`date +%s`
make get_results get_split_queries
if [ $? -ne 0 ] ; then
	MAKE_ERROR_CODE="$?"
	echo "ERROR: 'make get_results_only get_batches' failed: MAKE_ERROR_COD: E${MAKE_ERROR_CODE}" 
	make -C .. delete
	exit 1
fi	
tm1=`date +%s`
tm_elapsed=`expr $tm1 - $tm0`


echo "INFO: DELETING K8S CLUSTER"
# Delete cluster
make -C .. delete

echo "INFO: RETRIEVED RESULTS AND BATCHES. ELAPSED: $tm_elapsed SEC"
echo "INFO: DOWNLOADED_RESULTS: $DOWNLOADED_RESULTS"
echo "INFO: DOWNLOADED_QUERY_BATCHES: $DOWNLOADED_QUERY_BATCHES"


# FIXME: What is the rationale for this choice?
export MAX_NUM_THREADS=16
#===========================================================================
if [ ! -d ${DOWNLOADED_RESULTS} ] ; then
	echo "ERROR: CAN'T DOWNLOAD RESULTS TO $DOWNLOADED_RESULTS make get_results"
	exit 1
fi
RESULTS_COUNT=`ls -1 ./${DOWNLOADED_RESULTS}/batch_*.gz | wc -l`
if [ "X$RESULTS_COUNT" = "X" ] ; then
	echo "ERROR: CAN'T GET RESULTS COUNT FROM $DOWNLOADED_RESULTS"
	exit 1
fi	
echo "INFO: TOTAL RESULTS FILES IN THIS TEST: $RESULTS_COUNT"

# ATT: set BLASTDB here
export BLASTDB="./LOCAL_BLASTDB"

# STEP.  prepare local results directory
if [  -d "./local_results" ] ; then
	rm -rf ./local_results 
fi
mkdir ./local_results
if [ !  -d "./local_results" ] ; then
	echo "ERROR: can't create ./local_results"
	exit 1
fi	

# STEP: CHECK AND MAKE LOCAL COPY OF A FILE WITH QUERIES
gsutil  -q stat ${ELB_QUERIES} 
if [ $? -ne  0 ] ;  then
	echo "ERROR: QUERY FILE NOT FOUND: ${ELB_QUERIES}"
	exit 1
fi	

SHORT_QUERY_NAME=`basename $ELB_QUERIES`
gsutil -q cp ${ELB_QUERIES} "./local_results/${SHORT_QUERY_NAME}"

if [ ! -f "./local_results/${SHORT_QUERY_NAME}" ] ; then
	echo "ERROR: CAN'T COPY FILE WITH QIERIES LOCALLY TO THE  ./local_results/${SHORT_QUERY_NAME}"
	exit 1
fi	


DIFF_OK="NO"
RUN_OK="NO"

# STEP: GET ACTUAL USERS PARAMETERS FROM GENERATED YAML FILE
YAML_FILE="../blast_specs/blast-batch-000.yaml"
echo "INFO: GETTING PARAMETERS FOR LOCAL RUN..."
if [ ! -e  ${YAML_FILE}  ] ; then
	echo "ERROR: MISSING: ${YAML_FILE} PLEASE RERUN TEST FROM BEGINNING"
	exit 1
fi

#................................................................................................
#echo "TESTING: $YAML_FILE"
YAML_CMD_LINE=`cat $YAML_FILE | grep num_threads | cut -d} -f3- | sed -e 's/^ *- *//g'  | tr -d ';'`
PROG_CMD=`echo $YAML_CMD_LINE | awk '{ print $1}'`
# use wak: split command line by '-XYZ', remove out/query/num_threads/outfmt and print reset
EXTRA_PARAMS=`echo $YAML_CMD_LINE | awk '{ patsplit($0,keys,/ -[[:alpha:]_]+/,vals); ndx=1;while(keys[ndx]!=""){if(keys[ndx]==" -out"){}else if(keys[ndx]==" -query"){}else if(keys[ndx]==" -num_threads"){}else if(keys[ndx]==" -outfmt"){}else{printf("%s %s",keys[ndx],vals[ndx]);}ndx=ndx+1;} print ""}'`

echo "INFO: BLAST PROGRAM:     $PROG_CMD"
echo "INFO: USER EXTRA PARAMS: $EXTRA_PARAMS"

LOCAL_RUN_CMD="$PROG_CMD $EXTRA_PARAMS -query "./local_results/${SHORT_QUERY_NAME}" -out ./local_results/all_results.out -outfmt 6 -num_threads ${MAX_NUM_THREADS}"
echo "INFO: RUNNING LOCALLY: $LOCAL_RUN_CMD"
$LOCAL_RUN_CMD
RUN_ERROR_CODE=$?
if [ ${RUN_ERROR_CODE} -eq  0 ] ; then
	RUN_OK="YES"
else	
	echo "ERROR: LOCAL RUN FAILED. ERROR CODE: $RUN_ERROR_CODE"
	exit 1
fi

# STEP:  check results and sort them
if [ ! -e ./local_results/all_results.out ] ; then
	echo "ERROR: LOCAL RUN FAILED TO PRODUCE OUTPUT FILE:  ./local_results/all_results.out"
	exit 1
fi
# -- sort gcp results by e-value, column #11 ( 1 based )
zcat ./${DOWNLOADED_RESULTS}/batch_*.gz | sort -gk 11,11 > "./${DOWNLOADED_RESULTS}/gcp_all_results.sorted"
cat  ./local_results/all_results.out | sort -gk 11,11 > "./local_results/all_results.sorted"

LOCAL_DIFF_CMD="diff -b ./local_results/all_results.sorted ./${DOWNLOADED_RESULTS}/gcp_all_results.sorted "
diff ./local_results/all_results.sorted ./${DOWNLOADED_RESULTS}/gcp_all_results.sorted  > ./local_results/all.diff
if [ $? -eq 0 ] ; then
		DIFF_OK="YES"
fi

if [ -s  ./local_results/all.diff ] ; then
	RUN_OK="NO"
fi


if [ ${RUN_OK} != "YES" ] ; then
	echo "ERROR: THERE ARE DIFFERENCES BETWEEN ./local_results/all_results.sorted ./${DOWNLOADED_RESULTS}/gcp_all_results.sorted DIFF: ./local_results/all.diff"
	echo "FINAL:FAILED."
	exit 1
fi

echo "FINAL:PASSED"
exit 0

