#!/bin/bash -x
# share/tools/aws-list-vpc.sh: What this script does
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Mon 05 Apr 2021 04:03:41 PM EDT

export AWS_DEFAULT_OUTPUT="json"
export AWS_PAGER=''

for r in us-east-1 us-east-2 us-west-1 us-west-2; do
#for r in us-east-2 us-west-1 us-west-2; do
    echo "**********************************************************************"
    dflt_vpc=$(aws ec2 describe-vpcs --filters=Name=isDefault,Values=true --region $r | jq -Mr '.Vpcs[].VpcId')
    if [ ! -z "$dflt_vpc" ]; then
        aws ec2 describe-subnets --region $r --filters=Name=vpc-id,Values=$dlft_vpc
    else
        echo "No default VPC in $r, available VPC IDs"
        for vpc in $(aws ec2 describe-vpcs --filters=Name=isDefault,Values=false --region $r | jq -Mr '.Vpcs[].VpcId'); do
            aws ec2 describe-subnets --region $r --filters=Name=vpc-id,Values=$vpc | \
                jq -Mr '.Subnets[] | { SubnetId:.SubnetId, VpcId:.VpcId, AZ:.AvailabilityZone, NumIPs:.AvailableIpAddressCount, State:.State,Tags:.Tags} '
        done
    fi
done
