#!/bin/bash
# share/test/k8s-versions-delete.sh: Test various versions of kubectl client
# and server with ElasticBLAST for GCP
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Thu 27 Apr 2023 12:43:06 PM EDT

shopt -s nullglob
set -euo pipefail

k8s_install_path=${1:-~/local/bin}
k8s_server_version=1.25
ver=$(elastic-blast --version | cut -f 2 -d ' ')
if [[ $ver =~ post ]] ; then
    ver=develop
fi

CFG=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
trap " /bin/rm -fr $CFG " INT QUIT EXIT HUP KILL ALRM

for n in $(seq 18 25); do
    v=1.$n
    suffix=v${v}-srv-${k8s_server_version}-elb-${ver}
    cat > $CFG <<EOF
[cloud-provider]
gcp-region = us-east4
gcp-zone = us-east4-b
gke-version = ${k8s_server_version}

[cluster]
num-nodes = 1

[blast]
program = blastp
db = swissprot
queries = gs://elastic-blast-samples/queries/protein/BDQA01.1.fsa_aa
results = gs://elasticblast-$USER/results/BDQA-k8s-client-$suffix
options = -task blastp-fast -evalue 0.01 -outfmt "7 std sskingdoms ssciname"
EOF

    (cd $k8s_install_path && ln -sf kubectl-$v kubectl)
    ls -l `which kubectl`
    time elastic-blast delete --cfg $CFG --logfile elastic-blast-k8s-client-${suffix}.log
    gsutil ls -l -r gs://elasticblast-$USER/results/BDQA-k8s-client-${suffix}
done

