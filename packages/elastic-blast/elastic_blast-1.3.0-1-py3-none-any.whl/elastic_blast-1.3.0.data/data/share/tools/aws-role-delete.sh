#!/bin/bash
# aws-role-delete.sh: Deletes the role and instance profile created via
# aws-role-create.sh
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Tue Mar 23 15:41:23 2021

export PATH=/bin:/usr/local/bin:/usr/bin
set -xuo pipefail
shopt -s nullglob

role_name=${1:-"ElasticBlastTestRole-$USER"}
profile_name=${2:-"ElasticBlastTestInstanceProfile-$USER"}
policy_name=${3:-"ElasticBlastTestPolicy-$USER"}

acct=$(aws sts get-caller-identity --output json | jq -r .Account)
parn=arn:aws:iam::$acct:policy/$policy_name

aws iam remove-role-from-instance-profile --instance-profile-name $profile_name --role-name $role_name
aws iam detach-role-policy --role-name $role_name --policy-arn $parn
aws iam delete-role --role-name $role_name
aws iam delete-instance-profile --instance-profile-name $profile_name
