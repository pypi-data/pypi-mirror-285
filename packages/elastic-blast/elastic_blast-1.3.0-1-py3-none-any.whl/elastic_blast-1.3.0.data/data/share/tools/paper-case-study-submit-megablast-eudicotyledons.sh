#!/bin/bash

set -xeuo pipefail
shopt -s nullglob

[ -f submit-and-wait-for-results.sh ] || curl -sO https://raw.githubusercontent.com/ncbi/elastic-blast-demos/master/submit-and-wait-for-results.sh
[ -x submit-and-wait-for-results.sh ] || chmod +x submit-and-wait-for-results.sh

db=eudicotyledons
test_case=megablast-$db

TMP=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
trap " /bin/rm -fr $TMP " INT QUIT EXIT HUP KILL ALRM
cat > $TMP <<EOF
[cloud-provider]
aws-region = us-east-1

[cluster]
num-nodes = 100

[blast]
program = blastn
queries = eb1454.query-list
db = s3://elasticblast-test/db/plants/$db
results = s3://elasticblast-$USER/$test_case
options = -outfmt "6 qseqid sseqid pident slen length mismatch gapopen qlen qstart qend sstart send evalue bitscore score staxid" -evalue 1e-5 -perc_identity 75 -max_target_seqs 5 -max_hsps 10 -penalty -3
EOF

# N.B.: the script below is modified by hand to NOT download the results locally and test them
./submit-and-wait-for-results.sh $TMP 500 $test_case.log $test_case.json
