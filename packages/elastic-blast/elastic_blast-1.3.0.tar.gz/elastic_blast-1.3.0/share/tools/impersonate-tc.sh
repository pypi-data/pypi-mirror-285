#!/bin/bash -xe
# Script to "impresonate" TC and delete ElasticBLAST searches that are lingering
[ $# -lt 1 ] && { 
    echo "Usage: $0 <ELB_RESULTS> [ELB_GCP_ZONE]"; 
    echo "\tDefault ELB_GCP_ZONE=us-east4-b (if applicable)";
    exit 1 ; 
}

results2clustername() {
    elb_results=$1
    md5=md5sum
    command -v $md5 >& /dev/null || md5=md5
    results_hash=$(printf $elb_results | $md5 | cut -b-9)
    echo elasticblast-$USER-$results_hash
}

export USER=tomcat
export ELB_RESULTS=${1}
export ELB_CLUSTER_NAME=$(results2clustername $ELB_RESULTS)

if [[ $ELB_RESULTS =~ ^gs:// ]]; then
    export ELB_GCP_PROJECT=ncbi-sandbox-blast
    export ELB_GCP_ZONE=${2:-"us-east4-b"}
    export ELB_GCP_REGION=$(echo $ELB_GCP_ZONE | cut -b-8)
    export ELB_DONT_DELETE_SETUP_JOBS=1
    export KUBECONFIG=${PWD}/kubeconfig.yaml
fi

elastic-blast status --verbose --loglevel DEBUG --logfile stderr --results ${ELB_RESULTS}
elastic-blast delete --loglevel DEBUG --logfile stderr --results ${ELB_RESULTS}
