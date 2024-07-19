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
# gcp-create-svc-acct.sh: Script to facilitate creating a service account to
# run ElasticBLAST
# Created: Thu Nov 18 21:41:28 2021

set -euo pipefail
shopt -s nullglob

id=${1:-"elb-svc"}
prj_id=`gcloud config get-value project`
gcloud config get-value account

svc_acct=$id@$prj_id.iam.gserviceaccount.com

# If the service account already exists, exit this script
gcloud iam service-accounts describe $svc_acct && exit 0

gcloud iam service-accounts create $id \
    --description="ElasticBLAST service account" \
    --display-name="ElasticBLAST service account";

# Role roles/container.admin needed for "gcloud container clusters list" and ElasticBLAST janitor
# Role roles/storage.objectAdmin needed for writing to buckets and deleting ancillary data on buckets
# Role roles/compute.admin needed for "gcloud compute regions describe ", among other compute operations
# Role roles/iam.serviceAccountUser needed for "gcloud container clusters create" and the ability to access the service account for GCP's compute

for role in \
    roles/compute.admin \
    roles/container.admin \
    roles/storage.objectAdmin \
    roles/iam.serviceAccountUser;\
do
    gcloud projects add-iam-policy-binding $prj_id \
        --member="serviceAccount:$svc_acct" \
        --role=$role
done

sleep 120;  # Needed for the command below not to fail
[ -f $id-key.json ] || \
    gcloud iam service-accounts keys create $id-key.json \
            --iam-account=$svc_acct
