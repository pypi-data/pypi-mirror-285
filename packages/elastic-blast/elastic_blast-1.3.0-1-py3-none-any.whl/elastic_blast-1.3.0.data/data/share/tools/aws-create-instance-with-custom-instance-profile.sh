#!/bin/bash
# aws-create-instance-with-custom-instance-profile.sh: Creates an instance with a custom instance profile
#
# Author: Christiam Camacho (camacho@ncbi.nlm.nih.gov)
# Created: Wed Mar 24 15:16:47 2021

export PATH=/bin:/usr/local/bin:/usr/bin
set -xeuo pipefail
shopt -s nullglob

instance_profile=${1:-"ElasticBlastTestInstanceProfile-$USER"}
elb_version=${2:-"0.0.27"}
key_name=${3:-"elasticblast-$USER"}
aws_region=us-east-1
#subnet=${4:-`aws cloudformation describe-stacks --stack-name development-vpc --region $aws_region --query "Stacks[0].Outputs[?OutputKey=='PublicSubnet1'].OutputValue" --output text`}
#sgs=${5:-`aws cloudformation describe-stacks --stack-name development-vpc --region us-east-1 --query "Stacks[0].Outputs[?OutputKey=='SshPingIngressSecurityGroup'].OutputValue" --output text`}
subnet=${4:-"subnet-e6264580"}  # Obtained via aws ec2 describe-subnets --region us-east-1 --filters Name=vpc-id,Values=vpc-5b43ff26 | jq -r '.Subnets[] | .SubnetId'
sgs=${5:-"sg-017467cb427421f88"} # Obtained via slack from VJ
instance_type=c4.xlarge
#ami_id=ami-0c94855ba95c71c99
# Source: https://aws.amazon.com/blogs/compute/query-for-the-latest-amazon-linux-ami-ids-using-aws-systems-manager-parameter-store/
ami_id=$(aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 --query 'Parameters[0].[Value]' --output text)
name=elastic-blast-launcher-$USER

USER_DATA=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
TAGS=`mktemp -t $(basename -s .sh $0)-XXXXXXX`
trap " /bin/rm -fr $TAGS $USER_DATA " INT QUIT EXIT HUP KILL ALRM

cat >$TAGS<<EOF
[
    {
        "ResourceType": "volume",
        "Tags": [
            { "Key": "billingcode", "Value": "elastic-blast" },
            { "Key": "Project", "Value": "BLAST" },
            { "Key": "Owner", "Value": "$USER" },
            { "Key": "Name", "Value": "$name" }
        ]
    },
    {
        "ResourceType": "instance",
        "Tags": [
            { "Key": "billingcode", "Value": "elastic-blast" },
            { "Key": "Project", "Value": "BLAST" },
            { "Key": "Owner", "Value": "$USER" },
            { "Key": "Name", "Value": "$name" }
        ]
    }
]
EOF
cat -n $TAGS

cat >$USER_DATA<<EOF
#!/bin/bash -xe
yum update -y
yum install -y git
amazon-linux-extras install python3.8
[ -l /usr/bin/python3 ] || ln -s /usr/bin/python3.8 /usr/bin/python3

#curl -sO https://storage.googleapis.com/elastic-blast/release/${elb_version}/elastic-blast
#curl -sO https://storage.googleapis.com/elastic-blast/release/${elb_version}/elastic-blast.md5
#md5sum -c elastic-blast.md5
curl ftp://ftp.ncbi.nlm.nih.gov/blast/temp/camacho/elastic-blast
chmod +x elastic-blast
mv elastic-blast /usr/bin
/usr/bin/elastic-blast --version

EOF
cat -n $USER_DATA

aws ec2 run-instances \
    --region $aws_region \
    --image-id ${ami_id} \
    --instance-type ${instance_type} \
    --key-name ${key_name} \
    --subnet-id ${subnet} \
    --security-group-ids ${sgs} \
    --tag-specifications file://$TAGS \
    --count 1 \
    --iam-instance-profile Name=$instance_profile \
    --user-data file://${USER_DATA} \
    --query 'Instances[*].InstanceId' --output text \
    | tee iid.txt
