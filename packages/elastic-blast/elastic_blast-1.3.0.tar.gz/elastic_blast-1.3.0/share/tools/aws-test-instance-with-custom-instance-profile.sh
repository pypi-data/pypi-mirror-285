#!/bin/bash
# aws-test-instance-with-custom-instance-profile.sh: Runs elastic-blast on the instance created by aws-create-instance-with-custom-instance-profile.sh
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Wed Mar 24 15:50:03 2021

export PATH=/bin:/usr/local/bin:/usr/bin
set -xeuo pipefail
shopt -s nullglob

iid=${1:-`cat iid.txt`}
timeout=${2:-20}
dns=$(aws ec2 describe-instances --instance-ids `cat iid.txt` --output json --filters Name=instance-state-name,Values=running | \
    jq -r '.Reservations[].Instances[].PublicDnsName')

[ -z "$dns" ] && { echo "Instance is not available yet"; exit 1 ; }

SCRIPT=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
CFG=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
trap " /bin/rm -fr $CFG $SCRIPT " INT QUIT EXIT HUP KILL ALRM

cat >$CFG<<EOF
[cloud-provider]
aws-region = us-east-1

[cluster]
machine-type = m5.8xlarge
num-nodes = 1

[blast]
results = s3://elasticblast-$USER/test-results
program = blastn
db = pdbnt
queries = s3://elasticblast-test/queries/MANE.GRCh38.v0.8.select_refseq_rna.fna
EOF
scp $CFG ec2-user@$dns:elastic-blast.ini

cat >$SCRIPT<<EOF
#!/bin/bash -xe
aws configure list
aws sts get-caller-identity
[ -f submit-and-wait-for-results.sh ] || curl -sO https://raw.githubusercontent.com/ncbi/elastic-blast-demos/master/submit-and-wait-for-results.sh
[ -x submit-and-wait-for-results.sh ] || chmod +x submit-and-wait-for-results.sh

./submit-and-wait-for-results.sh elastic-blast.ini $timeout 
EOF
chmod +x $SCRIPT

scp $SCRIPT ec2-user@$dns:run-me.sh
ssh ec2-user@$dns nohup ./run-me.sh
