#!/bin/bash
# share/test/run-aws-quickstart.sh: Script to facilitate runnning the
# ElasticBLAST quickstart on AWS.
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Fri 23 Jun 2023 03:56:13 PM EDT

shopt -s nullglob
set -euo pipefail

results_bucket=${1:-s3://elasticblast-$USER}

aws s3 ls $results_bucket >&/dev/null || { echo "ERROR: the results bucket $results_bucket is inaccessible"; exit 1; }

CFG=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
trap " /bin/rm -fr $CFG " INT QUIT EXIT HUP KILL ALRM

aws sts get-caller-identity

# Uncomment the next 5 lines if you want to use elastic-blast from PyPI
#### [ -d .elb-venv ] && rm -fr .elb-venv
#### python3 -m venv .elb-venv
#### source .elb-venv/bin/activate
#### pip install wheel
#### pip install elastic-blast

which elastic-blast
elastic-blast --version
elastic-blast --help

aws s3 ls $results_bucket >&/dev/null || aws s3 mb $results_bucket

suffix=$(date +%F-%T | tr : -)

cat > $CFG <<EOF
[cloud-provider]
aws-region = us-east-1

[cluster]
num-nodes = 1
#num-nodes = 4
labels = owner=$USER

[blast]
program = blastp
db = swissprot
queries = s3://elasticblast-test/queries/BDQA01.1.fsa_aa
#queries = s3://elasticblast-test/queries/CABDUW01P.1.fsa_aa
#queries = s3://elasticblast-test/queries/AAAFNC01P.1.fsa_aa
results = $results_bucket/results/BDQA-$suffix
options = -task blastp-fast -evalue 0.01 -outfmt "7 std sskingdoms ssciname"
EOF

[ -f submit-and-wait-for-results.sh ] || curl -sO https://raw.githubusercontent.com/ncbi/elastic-blast-demos/master/submit-and-wait-for-results.sh
[ -x submit-and-wait-for-results.sh ] || chmod +x submit-and-wait-for-results.sh

./submit-and-wait-for-results.sh ${CFG}

