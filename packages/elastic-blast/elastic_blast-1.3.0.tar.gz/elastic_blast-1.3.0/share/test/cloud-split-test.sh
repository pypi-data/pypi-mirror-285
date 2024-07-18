#!/bin/bash -eu
# Bash script for EB-974, EB-1081
# Run share/test/cloud-split-test.sh s3://some-bucket disk-type
# where disk-type is either local-ssd or ebs
# Produces run summary files split-only-*-summary.json
# Uses config files share/etc/elb-aws-split-only-*.ini 
RESULTS_BUCKET=${1:-"s3://elasticblast-test"}
dt=${2:-local-ssd}
# Pass 1 for single AWS Batch job approach, 2 for dual AWS Batch job approach
approach=${3:-1}

export ELB_NO_SEARCH=1

if [ $approach -eq 1 ] ; then
    export ELB_USE_1_STAGE_CLOUD_SPLIT=1
else
    export ELB_USE_2_STAGE_CLOUD_SPLIT=1
fi

for ds in mane vht2 viralmeta; do
    cfg=share/etc/elb-aws-split-only-$dt-$ds.ini
    log=aws-aws-split-only-$dt-$ds-approach${approach}.log
    export ELB_RESULTS=$RESULTS_BUCKET/cloud_split/split-only-$dt-$ds-approach${approach}

    elastic-blast submit --cfg $cfg --loglevel DEBUG --logfile $log
    elastic-blast status --wait --cfg $cfg --loglevel DEBUG --logfile $log
    elastic-blast run-summary --cfg $cfg --write-logs split-only-$dt-$ds-approach${approach}.log -o split-only-$dt-$ds-approach${approach}-summary.json --loglevel DEBUG --logfile $log
    elastic-blast delete --cfg $cfg --loglevel DEBUG --logfile $log
done
