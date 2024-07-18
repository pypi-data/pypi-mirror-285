#!/bin/bash
# deploy-elastic-blast-docs.sh: Script to deploy ElasticBLAST documentation in NCBI hosts
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Wed 16 Dec 2020 10:31:11 AM EST

export PATH=/bin:/usr/local/bin:/usr/bin
set -euo pipefail
shopt -s nullglob

deployment_target="dev"
comment=''
dry_run=0
archive2deploy="elastic-blast-docs.tar.bz2"

DBALIASTEST=/net/blastdev11/export/home/blastadm/bin/dbaliastest
SDRELEASE=/net/snowman/vol/export4/blastqa/blastsoft_dev_setup_dir/sdrelease


echo "#############################################################"
echo NOTE: deployments to production COLO require an SSH tunnel to be created. Follow instructions for step 5 in http://intranet/cvsutils/index.cgi/internal/blast/interfaces/blast4/test_and_deployment_procedures.txt
echo "#############################################################"

while getopts "t:c:na:" OPT; do
    case $OPT in 
        a) archive2deploy=${OPTARG}
            ;;
        t) deployment_target=${OPTARG}
            ;;
        c) comment=${OPTARG}
            ;;
        n) dry_run=1
            ;;
    esac
done

# Some error checking
if [[ "$deployment_target" != "dev" ]] && [[ "$deployment_target" != "prod" ]] || [[ -z "$comment" ]] ; then
    echo "Usage: $0 -t [dev|prod] -c \"DEPLOYMENT COMMENT\""
    exit 1
fi
if [ ! -s $archive2deploy ] ; then
    echo $archive2deploy does not exist or is empty
    exit 1
fi
[ -f $DBALIASTEST ] || { echo FATAL ERROR: cannot find $DBALIASTEST; exit 1; }
[ -f $SDRELEASE ] || { echo FATAL ERROR: cannot find $SDRELEASE; exit 1; }

#  Hosts information should be obtained from *MachineTasking confluence page
TEST_HOSTS="testblast142,testblast143,testblast114"
BETH_PROD_HOSTS="blast520,blast525,blast902.be-md.qa"
COLO_PROD_HOSTS="blast3416.st-va,blast3420.st-va"
HOSTS=$TEST_HOSTS
if [[ "$deployment_target" == "prod" ]] ; then
    HOSTS=$BETH_PROD_HOSTS
fi

# Per Yan's suggestion
U=`$DBALIASTEST -s SD_DBLDD -a BLASTQ4 -r splitd_client|awk -F\; '{print $2}'`
P=`$DBALIASTEST -s SD_DBLDD -a BLASTQ4 -r splitd_client|awk -F\; '{print $3}'|tr -d ')'`

if [ $dry_run -eq 1 ] ; then
    echo $SDRELEASE -src $archive2deploy -dst $HOSTS -c \"$comment\"
else
    $SDRELEASE -U $U -P $P -src $archive2deploy -dst $HOSTS -c "$comment"
fi

# COLO is for production only
if [[ "$deployment_target" == "prod" ]] ; then
    HOSTS=$COLO_PROD_HOSTS
    if [ $dry_run -eq 1 ] ; then
        echo $SDRELEASE -src $archive2deploy -dst $HOSTS -c \"$comment\" -S 127.0.0.1
    else
        $SDRELEASE -U $U -P $P -src $archive2deploy -dst $HOSTS -c "$comment" -S 127.0.0.1
    fi

    echo Please check the URLs below:
    echo https://blast.be-md.ncbi.nlm.nih.gov/doc/elastic-blast
    echo https://blast.st-va.ncbi.nlm.nih.gov/doc/elastic-blast
else
    echo "Please check (from within NCBI) the following URL:"
    echo https://internal.ncbi.nlm.nih.gov/doc/elastic-blast
fi
