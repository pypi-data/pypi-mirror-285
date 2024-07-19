#!/bin/bash -xe
# Script to release ElasticBLAST code from system of record (bitbucket) to
# github
#
# Author: Victor Joukov

set -u

branch="latest"
deployment_target="dev"
system_of_record="ssh://git@bitbucket.be-md.ncbi.nlm.nih.gov:9418/blast/elastic-blast.git"

while getopts "t:b:" OPT; do
    case $OPT in 
        b) branch=${OPTARG}
            ;;
        t) deployment_target=${OPTARG}
            ;;
    esac
done

# Some error checking
if [[ "$deployment_target" != "dev" ]] && [[ "$deployment_target" != "prod" ]]; then
    echo "Usage: $0 -t [dev|prod] -b BRANCH_TO_RELEASE"
    exit 1
fi
if [[ "$deployment_target" == "dev" ]]; then
    external_repo=git@github.com:victzh/elastic-blast.git
else
    external_repo=git@github.com:ncbi/elastic-blast.git
fi


src=`mktemp -d`
dst=`mktemp -d`
exclusions=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
inclusions=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
# For debugging
#trap "cd ; ls -lR $dst/share $dst/.git $dst/bin $dst/docs; /bin/rm -fr $src $dst $inclusions $exclusions " INT QUIT EXIT HUP KILL ALRM
trap "/bin/rm -fr $src $dst $inclusions $exclusions " INT QUIT EXIT HUP KILL ALRM

# These paths (except .git) will be deleted from final output
cat >$exclusions<<EOF
.git
.teamcity
.aws_login
share
demo
setenv.sh
elb-cost.py
cost.py
test_cost.py
gcp_ram_size.py
README-elb-cost.md
README-ncbi.md
README-blast-tuner.md
performance
Makefile-pypi
aws-elastic-blast-number-of-nodes.sh
submit-elb-for-janitor-update.sh
EOF

if [ "$branch"  = "latest" ] ; then
    git clone -q $system_of_record $src
else
    git clone -q -b $branch $system_of_record $src
fi
git clone -q $external_repo $dst

rsync -Cvac --delete-after --exclude-from=$exclusions $src/ $dst/
for f in `egrep -v .git $exclusions`; do
    find $dst -name "$f" | xargs rm -frv
done

cat >$inclusions<<EOF
share/etc/elastic-blast-aws-iam-policy.json.template
share/etc/yamllint-config.yaml
share/etc/elb-aws-blastn-nt-8-nodes.ini
share/etc/elb-blastp-nr.ini
EOF
rsync -Cvac --files-from=$inclusions $src/ $dst/

cd $dst
mv Makefile-public Makefile
sed -i -e '/ncbi-sandbox-blast/d' share/etc/*.ini
sed -i -e 's/^PYTHON_VERSION.*/PYTHON_VERSION=3/' Makefile
git add -A
git commit -m "Release $branch"
git push -q
git tag -d $branch && git push --delete origin $branch || true
git tag -a $branch -m "Release $branch"
git push origin $branch
