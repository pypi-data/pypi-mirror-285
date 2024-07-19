#!/bin/bash
# aws-role-create.sh: Create and tag role
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Tue Mar 23 15:41:23 2021

export PATH=/bin:/usr/local/bin:/usr/bin
set -xeuo pipefail
shopt -s nullglob

role_name=${1:-"ElasticBlastTestRole-$USER"}
profile_name=${2:-"ElasticBlastTestInstanceProfile-$USER"}
policy_name=${3:-"ElasticBlastTestPolicy-$USER"}

acct=$(aws sts get-caller-identity --output json | jq -r .Account)
parn=arn:aws:iam::$acct:policy/$policy_name

TMP=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
trap " /bin/rm -fr $TMP " INT QUIT EXIT HUP KILL ALRM
# Create the trust policy file
cat >$TMP<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
        "Sid": "",
        "Effect": "Allow",
        "Principal": { "Service": "ec2.amazonaws.com" },
        "Action": "sts:AssumeRole"
      }
  ]
}
EOF
cat -n $TMP
aws iam create-role --role-name $role_name --assume-role-policy-document file://$TMP
aws iam tag-role --role-name $role_name --tags Key=Name,Value=$role_name
aws iam tag-role --role-name $role_name --tags Key=Owner,Value=$USER
aws iam tag-role --role-name $role_name --tags Key=billingcode,Value=elastic-blast
aws iam attach-role-policy --role-name $role_name --policy-arn $parn

aws iam create-instance-profile --instance-profile-name $profile_name
aws iam tag-instance-profile --instance-profile-name $profile_name --tags Key=Name,Value=$profile_name
aws iam tag-instance-profile --instance-profile-name $profile_name --tags Key=Owner,Value=$USER
aws iam tag-instance-profile --instance-profile-name $profile_name --tags Key=billingcode,Value=elastic-blast
aws iam add-role-to-instance-profile --instance-profile-name $profile_name --role-name $role_name
