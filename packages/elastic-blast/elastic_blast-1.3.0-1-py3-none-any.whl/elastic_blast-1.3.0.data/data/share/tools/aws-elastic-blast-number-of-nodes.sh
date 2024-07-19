#!/bin/bash
# share/tools/aws-elastic-blast-number-of-nodes.sh: Script to query and set the
# number of nodes in an ElasticBLAST search
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Fri 25 Feb 2022 09:53:43 AM EST

set -euo pipefail
shopt -s nullglob

command -v aws >&/dev/null || { echo "aws must be in your PATH for this script to work"; exit 1; }
command -v results2clustername.sh >&/dev/null || { echo "results2clustername.sh must be in your PATH for this script to work"; exit 1; }

usage() {
    echo -e "$0 [-h] -r ELB_RESULTS [-n N]\n"
    echo -e "This script displays or updates the number of nodes assigned to a given ElasticBLAST search\n";
    echo -e "Options:"
    echo -e "\t-r ELB_RESULTS: ElasticBLAST search results bucket"
    echo -e "\t-n N: If greater than the current number of nodes, it increases the number of nodes for a given ElasticBLAST search. If omitted, prints the number of nodes in the current configuration"
    echo -e "\t-h: Show this message"
}

[ $# -eq 0 ] && { usage; exit 0; }
target_num_nodes=0

while getopts "r:n:h" OPT; do
    case $OPT in 
        r) elb_results=${OPTARG}
            ;;
        n) target_num_nodes=${OPTARG}
            ;;
        h) usage
           exit 0
            ;;
    esac
done

ce=$(results2clustername.sh $elb_results)
current_max_vcpus=`aws batch describe-compute-environments --compute-environment ${ce} --output text --query 'computeEnvironments[*].computeResources.maxvCpus'`
if [ ! -z "$current_max_vcpus" ] ; then
    instance_type=`aws batch describe-compute-environments --compute-environment ${ce} --output text --query 'computeEnvironments[*].computeResources.instanceTypes[0]'`
    cpus_per_instance=`aws ec2 describe-instance-types --instance-types $instance_type --output text --query 'InstanceTypes[*].VCpuInfo.DefaultVCpus'`
    num_nodes=$(( ${current_max_vcpus} / ${cpus_per_instance} ))

    if [ $target_num_nodes -eq 0 ] ; then
        echo "Current number of ${instance_type} nodes: $num_nodes"
        echo "Current maximum vCPUs: $current_max_vcpus ($cpus_per_instance vCPUs per instance)"
        exit 0
    fi

    if [ $target_num_nodes -gt $num_nodes ] ; then
        target_max_vcpus=$(( $cpus_per_instance * ${target_num_nodes} ))
        echo "Target num nodes: $target_num_nodes"
        echo "Target maximum vCPUs: $target_max_vcpus"
        aws batch update-compute-environment --compute-environment ${ce} --compute-resources maxvCpus=$target_max_vcpus
    else
        echo "ERROR: Cannot reduce the number of nodes from $num_nodes to $target_num_nodes"
        exit 1
    fi
else
    echo "ERROR: No ElasticBLAST search exists with results in $elb_results"
    exit 1
fi
