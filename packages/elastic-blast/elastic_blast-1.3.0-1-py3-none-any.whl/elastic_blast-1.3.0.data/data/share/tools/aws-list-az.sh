#!/bin/bash
# share/tools/aws-list-as.sh: Show number of Availability zones for regions
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Mon 05 Apr 2021 03:40:17 PM EDT

for r in us-east-1 us-east-2 us-west-1 us-west-2; do
    n=`aws ec2 describe-availability-zones --region $r --output json | jq -r '.AvailabilityZones[].ZoneName' |wc -l`
    echo "$r $n zones"
done
