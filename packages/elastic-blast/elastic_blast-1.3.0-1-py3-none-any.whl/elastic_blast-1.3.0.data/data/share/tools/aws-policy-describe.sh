#!/bin/bash -e
# aws-policy-describe.sh: Retrieves the last few policy versions for the given
# AWS IAM policy
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Wed Mar 24 15:03:54 2021

set -euo pipefail

policy_name=${1:-"ElasticBlastTestPolicy-$USER"}
acct=$(aws sts get-caller-identity --output json | jq -r .Account)
parn=arn:aws:iam::$acct:policy/$policy_name
v=`aws iam get-policy --policy-arn $parn --output json | jq -r .Policy.DefaultVersionId`
aws iam get-policy-version --policy-arn $parn --version-id $v | tee elb-policy.json
vn=$(echo $v | tr -d v)
le=$(($vn - 5))
for n in $(seq $le $vn); do
    o=elb-policyv$n.json
    [ -f $o ] || aws iam get-policy-version --policy-arn $parn --version-id v$n | tee $o
done
