#!/bin/bash
# aws-policy-create.sh: Creates the policy specified by the file name
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Fri Mar 26 18:28:32 2021

export PATH=/bin:/usr/local/bin:/usr/bin
set -xeuo pipefail
shopt -s nullglob

pname=${1:-"ElasticBlastTestPolicy-$USER"}
policy_file=${2:-iam-policy.json}
parn=$(
    aws iam create-policy \
        --policy-name $pname \
        --policy-document file://$policy_file | tee | jq -r .Policy.Arn
)
aws iam tag-policy --policy-arn $parn --tags Key=Name,Value=$pname
aws iam tag-policy --policy-arn $parn --tags Key=Owner,Value=$USER
aws iam tag-policy --policy-arn $parn --tags Key=billingcode,Value=elastic-blast
