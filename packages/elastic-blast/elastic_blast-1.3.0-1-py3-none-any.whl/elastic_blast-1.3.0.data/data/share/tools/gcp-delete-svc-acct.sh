#!/bin/bash
#                           PUBLIC DOMAIN NOTICE
#              National Center for Biotechnology Information
#  
# This software is a "United States Government Work" under the
# terms of the United States Copyright Act.  It was written as part of
# the authors' official duties as United States Government employees and
# thus cannot be copyrighted.  This software is freely available
# to the public for use.  The National Library of Medicine and the U.S.
# Government have not placed any restriction on its use or reproduction.
#   
# Although all reasonable efforts have been taken to ensure the accuracy
# and reliability of the software and data, the NLM and the U.S.
# Government do not and cannot warrant the performance or results that
# may be obtained by using this software or data.  The NLM and the U.S.
# Government disclaim all warranties, express or implied, including
# warranties of performance, merchantability or fitness for any particular
# purpose.
#   
# Please cite NCBI in any work or product based on this material.
#
# gcp-delete-svc-acct.sh: Deletes the service account created with gcp-create-svc-acct.sh
# Created: Thu Nov 18 21:41:28 2021

set -euo pipefail
shopt -s nullglob

id=${1:-"elb-svc"}
prj_id=`gcloud config get-value project`
gcloud config get-value account

svc_acct=$id@$prj_id.iam.gserviceaccount.com

gcloud iam service-accounts describe $svc_acct
gcloud iam service-accounts disable $svc_acct
gcloud iam service-accounts describe $svc_acct
for role in \
    roles/compute.admin \
    roles/container.admin \
    roles/storage.objectAdmin \
    roles/iam.serviceAccountUser; \
do
    gcloud projects remove-iam-policy-binding $prj_id \
        --member="serviceAccount:$svc_acct" \
        --role=$role
done

for key_id in `gcloud iam service-accounts keys list --iam-account=$sa | grep -v ^KEY_ID | awk '{print $1}'`; do
    gcloud iam service-accounts keys delete $key_id \
        --iam-account=$svc_acct
done

rm -f $id-key.json

gcloud iam service-accounts describe $svc_acct
yes | gcloud iam service-accounts delete $svc_acct
