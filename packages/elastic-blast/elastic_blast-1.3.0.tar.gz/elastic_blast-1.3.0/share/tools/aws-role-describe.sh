#!/bin/bash
# aws-role-describe.sh: Describe the role and instance profile provided
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Tue Mar 23 15:41:23 2021

export PATH=/bin:/usr/local/bin:/usr/bin
set -xuo pipefail
shopt -s nullglob

role_name=${1:-"ElasticBlastTestRole-$USER"}
profile_name=${2:-"ElasticBlastTestInstanceProfile-$USER"}
aws iam get-role --role-name $role_name --output json
aws iam get-instance-profile --instance-profile-name $profile_name --output json
