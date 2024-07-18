#!/bin/bash
# aws-delete-instance-with-custom-instance-profile.sh: Delete instance started by aws-create-instance-with-custom-instance-profile.sh
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Wed Mar 24 15:44:22 2021

export PATH=/bin:/usr/local/bin:/usr/bin
set -euo pipefail
shopt -s nullglob

iid=${1:-`cat iid.txt`}
region=${2:-"us-east-1"}
aws ec2 terminate-instances --instance-ids $iid --region $region
