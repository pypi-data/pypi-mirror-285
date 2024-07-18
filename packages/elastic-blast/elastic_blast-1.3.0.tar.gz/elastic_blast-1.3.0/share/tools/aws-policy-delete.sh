#!/bin/bash
# aws-policy-delete.sh: Deletes the policy specified
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Fri Mar 26 18:28:32 2021

export PATH=/bin:/usr/local/bin:/usr/bin
set -euo pipefail
shopt -s nullglob

pname=${1:-"ElasticBlastTestPolicy-$USER"}
acct=$(aws sts get-caller-identity --output json | jq -r .Account)
parn=arn:aws:iam::$acct:policy/$pname
aws iam delete-policy --policy-arn $parn 
