#                           PUBLIC DOMAIN NOTICE
#              National Center for Biotechnology Information
#  
# This software is a "United States Government Work" under the
# terms of the United States Copyright Act.  It was written as part of
# the authors' official duties as United States Government employees and
# thus cannot be copyrighted.  This software is freely available
# to the public for use.  The National Library of Medicine and the U.S.
# Government have not placed any restriction on its use or reproduction.
#   
# Although all reasonable efforts have been taken to ensure the accuracy
# and reliability of the software and data, the NLM and the U.S.
# Government do not and cannot warrant the performance or results that
# may be obtained by using this software or data.  The NLM and the U.S.
# Government disclaim all warranties, express or implied, including
# warranties of performance, merchantability or fitness for any particular
# purpose.
#   
# Please cite NCBI in any work or product based on this material.

# Makefile

SHELL=/bin/bash
.PHONY: init delete clean
.PHONY: test smoke_test clear_results get_results test_asn_results
.PHONY: distclean logs monitor show_config
.PHONY: list_resources top ps download_split_queries
.PHONY: credentials check_setup_job

SCRIPTS = elastic-blast elb-cost.py blast-tuner.py
VENV?=.env

BLAST_USAGE_REPORT=false

# Cluster/GCP configuration
ELB_CLUSTER_NAME?=`make -s results2clustername`
ELB_NUM_NODES?=1
# FIXME: should this be made the default? Allow enabling via env. var.? Something else? EB-297
ELB_USE_PREEMPTIBLE?=

ELB_AWS_REGION?=us-east-1

# See delete target
ELB_CONFIG_FILE?=

# BLAST configuration
ELB_BLAST_PROGRAM?=blastn
ELB_DB?=pdbnt

# Input/output configuration
ELB_QUERIES ?= gs://elastic-blast-samples/queries/MANE/MANE.GRCh38.v0.8.select_refseq_rna.fna
ELB_RESULTS ?= gs://elasticblast-${USER}

QUERY_BATCHES = ${ELB_RESULTS}/query_batches

ELB_LOGFILE ?= `pwd`/elastic-blast.log


include Makefile-public

#############################################################################
# build targets

APPS = $(basename $(SCRIPTS))
.PHONY: apps
apps: ${APPS} 

elb-cost: ${PYTHON_SRC} ${VENV}
	source ${VENV}/bin/activate && pex --disable-cache . -r requirements/base.txt --python=python${PYTHON_VERSION} -c $@.py -o $@
	-./$@ --version

#############################################################################
# gcloud/k8s targets

init:
	@if [ "${ELB_GCP_PROJECT}" == "" ] ; then echo "ELB_GCP_PROJECT environment variable must be defined"; exit 1; fi
	@if [ "${ELB_GCP_ZONE}" == "" ] ; then echo "ELB_GCP_ZONE environment variable must be defined"; exit 1; fi
	@if [ "${ELB_GCP_REGION}" == "" ] ; then echo "ELB_GCP_REGION environment variable must be defined"; exit 1; fi
	gcloud config set project ${ELB_GCP_PROJECT}
	gcloud config set compute/zone ${ELB_GCP_ZONE}
	gcloud config set compute/region ${ELB_GCP_REGION}
	command -v kubectl >&/dev/null
	command -v python3 >&/dev/null

credentials: init
	gcloud container clusters get-credentials ${ELB_CLUSTER_NAME}

delete: elastic-blast
	[ ! -z "${ELB_CONFIG_FILE}" ] || { echo "ELB_CONFIG_FILE environment variable must be defined"; exit 1; }
	-./elastic-blast delete --loglevel DEBUG --logfile stderr --cfg ${ELB_CONFIG_FILE}

clear_jobs: credentials
	-kubectl delete job -l app=test
	-kubectl delete job -l app=blast
	-kubectl delete job -l app=setup

# install kubectl
kubectl:
	curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
	chmod +x ./kubectl


#############################################################################
# Testing targets
smoke_test: ${VENV} check_version_help pylint mypy cfn-lint yamllint blast-tuner-smoke-test test_summary test-janitor
	source ${VENV}/bin/activate && python3 -m py_compile ${PYTHON_SRC} share/tools/run-report.py share/tools/cleanup-stale-gcp-resources.py share/tools/iam-policy-patcher.py
	source ${VENV}/bin/activate && pytest -vx
	source ${VENV}/bin/activate && fasta_split.py <(blastdbcmd -entry NC_000001 -db 9606_genomic) -o /tmp -t src/elastic_blast/templates/blast-batch-job.yaml.template && [ -f /tmp/batch_000.fa ];
	${RM} /tmp/batch_000.fa
	# Test batch length that exactly matches length of the first batch
	source ${VENV}/bin/activate && TEST_BATCH_LENGTH=1960 pytest $(shell find . -name test_fasta_split.py) -k TestSplitResultMatchesOriginal
	# EB-108 test case
	source ${VENV}/bin/activate && TEST_URL=gs://elastic-blast-samples/queries/protein/dark-matter-1M.faa.gz TEST_BATCH_LENGTH=20000 pytest $(shell find . -name test_fasta_split.py) -k TestSplitResultMatchesOriginal


.PHONY: check_version_help
check_version_help: ${VENV}
	for app in ${SCRIPTS}; do source ${VENV}/bin/activate && $$app --version; done
	for app in ${SCRIPTS} share/tools/*.py; do source ${VENV}/bin/activate && $$app -h; done

gcp_test_resubmission_to_same_results_bucket: elastic-blast
	tests/tc-bash-runner.sh tests/test-resubmission-to-same-results-bucket.sh share/etc/elb-blastn-pdbnt.ini
aws_test_resubmission_to_same_results_bucket: elastic-blast
	tests/tc-bash-runner.sh tests/test-resubmission-to-same-results-bucket.sh share/etc/elb-aws-blastn-pdbnt.ini

ELB_TEST_TIMEOUT_HEPATITIS_VS_NT?=95
ELB_TEST_TIMEOUT_MANE_VS_PDBNT?=15
ELB_TEST_TIMEOUT_MANE_VS_PDBNT_OPTIMAL_INSTANCE_TYPE?=30
ELB_TEST_TIMEOUT_COALA_VS_NR?=120
ELB_TEST_TIMEOUT_BLASTP_VIRAL_METAGENOME_VS_NR?=130
ELB_TEST_TIMEOUT_BLASTX_WB4_2_0811_VS_NR=180
ELB_TEST_TIMEOUT_TBLASTN_VIRAL_META_VS_NT=90
ELB_TEST_TIMEOUT_TBLASTX_BDQE01=45
ELB_TEST_TIMEOUT_RPSBLAST_AMR=40
ELB_TEST_TIMEOUT_RPSTBLASTN_WB4_2_0811=30
ELB_TEST_TIMEOUT_VIRAL_METAGENOMES_VS_SWISSPROT?=40
ELB_TEST_TIMEOUT_ALGAE_BACTERIUM_VS_NR?=6000
ELB_TEST_TIMEOUT_CORONAVIRUS_VS_ITSELF?=20
ELB_TEST_TIMEOUT_DB_DOWNLOAD?=60
ELB_TEST_TIMEOUT_JAERS_VS_NR?=300
#ELB_TEST_TIMEOUT_CORONAVIRUS_VS_NT?=120
ELB_TEST_TIMEOUT_RPSTBLASTN_FIVE?=86400
ELB_TEST_TIMEOUT_BLASTP_NR_DARK_MATTER?=480
ELB_TEST_TIMEOUT_BLASTX_NR_JAERSN01?=480
ELB_TEST_TIMEOUT_BLASTN_REFSEQ_RNA_RFQT01?=20
ELB_TEST_TIMEOUT_CONTAM_SCREEN?=480

ELB_TEST_TIMEOUT_BLASTN_NOPAL?=90
# Based on EB-719: 20% more than 90 hours
ELB_TEST_TIMEOUT_BLASTX_NOPAL?=388800 
# Based on EB-718: 20% more than 13h:20m (i.e.: 960 mins)
ELB_TEST_TIMEOUT_BLASTP_NOPAL?=960 
# Based on EB-936: 20% more than 6h (i.e.: 360 mins)
ELB_TEST_TIMEOUT_MEGABLAST_SRA_SPOTS_VS_REFSEQ_GENOMES?=432
# Based on EB-993: 20% more than 8h (i.e.: 480 mins)
ELB_TEST_TIMEOUT_BLASTP_DARK_MATTER?=576

ELB_TEST_TIMEOUT_BLASTN_16S_CHICKEN_GUT_METAGENOME?=10300 # Based on EB-736: 20% more than 143h (i.e.: 8,580 mins)
ELB_TEST_TIMEOUT_BLASTP_VIRAL_METAGENOMES_VS_NR?=15552 # Based on EB-955: 20% more than 216h (i.e.: 12,960 mins)

ELB_TEST_TIMEOUT_BLASTP_NR_SMALL_DARK_MATTER?=45

ELB_TEST_TIMEOUT_OUT_OF_MEM_EXPECTED_FAILURE?=15
ELB_TEST_TIMEOUT_OUT_OF_MEM_EXPECTED_FAILURE_DB?=10

#############################################################################
# Real world, performance tests

.PHONY: aws_regression_blastn_16s_chicken_gut_metagenome
aws_regression_blastn_16s_chicken_gut_metagenome: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-chicken-gut-metagenome.ini ${ELB_TEST_TIMEOUT_BLASTN_16S_CHICKEN_GUT_METAGENOME}

.PHONY: gcp_regression_blastn_16s_chicken_gut_metagenome
gcp_regression_blastn_16s_chicken_gut_metagenome: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-chicken-gut-metagenome-autoscale.ini ${ELB_TEST_TIMEOUT_BLASTN_16S_CHICKEN_GUT_METAGENOME}

.PHONY: aws_regression_blastn_nopal
aws_regression_blastn_nopal: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-nopal-transcriptome.ini ${ELB_TEST_TIMEOUT_BLASTN_NOPAL}

.PHONY: aws_regression_blastx_nopal
aws_regression_blastx_nopal: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastx-nopal-transcriptome.ini ${ELB_TEST_TIMEOUT_BLASTX_NOPAL}

.PHONY: aws_regression_blastp_nopal
aws_regression_blastp_nopal: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastp-nopal-transcriptome.ini ${ELB_TEST_TIMEOUT_BLASTP_NOPAL}

.PHONY: gcp_regression_blastn_nopal
gcp_regression_blastn_nopal: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-nopal-transcriptome.ini ${ELB_TEST_TIMEOUT_BLASTN_NOPAL}

.PHONY: gcp_regression_blastx_nopal
gcp_regression_blastx_nopal: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastx-nopal-transcriptome.ini ${ELB_TEST_TIMEOUT_BLASTX_NOPAL}

.PHONY: gcp_regression_blastp_nopal
gcp_regression_blastp_nopal: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastp-nopal-transcriptome.ini ${ELB_TEST_TIMEOUT_BLASTP_NOPAL}

#############################################################################

.PHONY: regression_nr_vs_algae_bacterium_multi_node
regression_nr_vs_algae_bacterium_multi_node: elastic-blast
	ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-psiblast-nr.ini ${ELB_TEST_TIMEOUT_ALGAE_BACTERIUM_VS_NR}

.PHONY: regression_psiblast_swissprot_vs_viral_metagenomes
regression_psiblast_swissprot_vs_viral_metagenomes: elastic-blast
	ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-psiblast-swissprot.ini ${ELB_TEST_TIMEOUT_VIRAL_METAGENOMES_VS_SWISSPROT}

.PHONY: regression_coronavirus
regression_coronavirus: elastic-blast
	ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-nt-coronaviridae.ini ${ELB_TEST_TIMEOUT_CORONAVIRUS_VS_ITSELF}

# Test creation of VPC with as many subnets as there are AZs in a region and spot instances
.PHONY: aws_regression_pdbnt_vs_mane_multi_node_create_resources_all_azs_spot
aws_regression_pdbnt_vs_mane_multi_node_create_resources_all_azs_spot: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-pdbnt-s3-query-create-resources-small-instance.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}

.PHONY: aws_regression_pdbnt_vs_mane_single_node_create_resources
aws_regression_pdbnt_vs_mane_single_node_create_resources: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-pdbnt-s3-query-create-resources.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}

.PHONY: aws_regression_blastn_non_default_params
aws_regression_blastn_non_default_params: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-non-default-params.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}
	test $$(zcat batch_000-blastn-pdbnt.out.gz | wc -l) -eq 5 

.PHONY: aws_regression_pdbnt_vs_mane_single_node
aws_regression_pdbnt_vs_mane_single_node: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-pdbnt.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}

.PHONY: aws_regression_pdbnt_vs_mane_optimal_instance_type
aws_regression_pdbnt_vs_mane_optimal_instance_type: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-spot-optimal-instance-type-blastn-pdbnt.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT_OPTIMAL_INSTANCE_TYPE}

.PHONY: aws_regression_nt_vs_hepatitis_multi_node
aws_regression_nt_vs_hepatitis_multi_node: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-nt-8-nodes.ini ${ELB_TEST_TIMEOUT_HEPATITIS_VS_NT}

.PHONY: aws_regression_blastp_nr_vs_small_dark_matter
aws_regression_blastp_nr_vs_small_dark_matter: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastp-nr-small-dark-matter.ini ${ELB_TEST_TIMEOUT_BLASTP_NR_SMALL_DARK_MATTER}

.PHONY: aws_regression_blastx_nr_vs_jaers01
aws_regression_blastx_nr_vs_jaers01: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastx-jaersn01.ini ${ELB_TEST_TIMEOUT_BLASTX_NR_JAERSN01}

.PHONY: aws_regression_blastn_refseq_rna_vs_rfqt01_nvme
aws_regression_blastn_refseq_rna_vs_rfqt01_nvme: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-refseq_rna-nvme.ini ${ELB_TEST_TIMEOUT_BLASTN_REFSEQ_RNA_RFQT01}

.PHONY: aws_regression_blastp_pataa_vs_dark_matter_multi_node
aws_regression_blastp_pataa_vs_dark_matter_multi_node: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastp-nr-s3-query-create-resources.ini ${ELB_TEST_TIMEOUT_HEPATITIS_VS_NT}

.PHONY: aws_regression_blastn_taxid_filtering
aws_regression_blastn_taxid_filtering: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-taxidfiltering.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}
	test $$(zcat batch_000-blastn-pdbnt.out.gz | grep 246196 | wc -l) -gt 0
	test $$(zcat batch_000-blastn-pdbnt.out.gz | grep 3562 | wc -l) -gt 0
	test $$(zcat batch_000-blastn-pdbnt.out.gz | cut -f 13 | sort | uniq | wc -l) -eq 2 

.PHONY: aws_regression_blastn_neg_taxid_filtering
aws_regression_blastn_neg_taxid_filtering: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-neg-taxidfiltering.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}
	test $$(zcat batch_000-blastn-pdbnt.out.gz | grep 246196 | wc -l) -eq 0
	test $$(zcat batch_000-blastn-pdbnt.out.gz | grep 93061 | wc -l) -eq 0
	test $$(zcat batch_000-blastn-pdbnt.out.gz | cut -f 13 | sort -u | wc -l) -gt 1

.PHONY: aws_regression_blastn_multi_file
aws_regression_blastn_multi_file: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-multiple-query-files.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}
	test $$(cat batch_00*.fa | awk '/>/ {print substr($$L, 1, 11);}' | grep SRR5665118 | wc -l) -gt 0
	test $$(cat batch_00*.fa | awk '/>/ {print substr($$L, 1, 11);}' | grep SRR5665119 | wc -l) -gt 0
	test $$(cat batch_00*.fa | awk '/>/ {print substr($$L, 1, 11);}' | grep RFQT0100 | wc -l) -gt 0

.PHONY: aws_regression_failed_db_download
aws_regression_failed_db_download: DO_NOT_TEST_RESULTS=1
aws_regression_failed_db_download: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastn-corrupted-db.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}
	test $$(aws batch describe-jobs --jobs $$(cat k8s.log | grep ^job | grep FAILED | cut -f 2) | jq .jobs[0].attempts[].container.taskArn | wc -l) -gt 1

.PHONY: regression_blastn_multi_file
regression_blastn_multi_file: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
	ELB_USE_CLIENT_SPLIT=1 \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-multiple-query-files.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}
	test `zgrep -c SRR5665118 batch_0*-blastn-pdbnt.out.gz | cut -f 2 -d ':' | awk '{s+=$$1;} END {print s;}'` -ge 53
	test `zgrep -c SRR5665119 batch_0*-blastn-pdbnt.out.gz | cut -f 2 -d ':' | awk '{s+=$$1;} END {print s;}'` -ge 713
	test `zgrep -c RFQT0100   batch_0*-blastn-pdbnt.out.gz | cut -f 2 -d ':' | awk '{s+=$$1;} END {print s;}'` -ge 42

.PHONY: regression_blastn_taxid_filtering
regression_blastn_taxid_filtering: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-taxidfiltering.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}
	test $$(zcat batch_000-blastn-pdbnt.out.gz | grep 246196 | wc -l) -gt 0
	test $$(zcat batch_000-blastn-pdbnt.out.gz | grep 3562 | wc -l) -gt 0
	test $$(zcat batch_000-blastn-pdbnt.out.gz | cut -f 13 | sort | uniq | wc -l) -eq 2 

.PHONY: regression_blastn_neg_taxid_filtering
regression_blastn_neg_taxid_filtering: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-neg-taxidfiltering.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}
	test $$(zcat batch_000-blastn-pdbnt.out.gz | grep 246196 | wc -l) -eq 0
	test $$(zcat batch_000-blastn-pdbnt.out.gz | grep 93061 | wc -l) -eq 0
	test $$(zcat batch_000-blastn-pdbnt.out.gz | cut -f 13 | sort -u | wc -l) -gt 1

.PHONY: regression_nt_vs_hepatitis_multi_node
regression_nt_vs_hepatitis_multi_node: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-nt-eb239.ini ${ELB_TEST_TIMEOUT_HEPATITIS_VS_NT}

.PHONY: regression_tblastx_BDQE01_vs_ref_virus_multi_node
regression_tblastx_BDQE01_vs_ref_virus_multi_node: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-tblastx-virusrep.ini ${ELB_TEST_TIMEOUT_TBLASTX_BDQE01}

.PHONY: regression_nr_vs_coala_multi_node
regression_nr_vs_coala_multi_node: elastic-blast
	#ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	#ELB_RESULTS=${ELB_RESULTS} \
	#	tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-slava-blastp-nr.ini ${ELB_TEST_TIMEOUT_COALA_VS_NR}
	true

.PHONY: regression_blastp_nr_vs_viral_metagenome
regression_nr_vs_viral_metagenome_multi_node: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastp-nr-viral-metagenome.ini ${ELB_TEST_TIMEOUT_BLASTP_VIRAL_METAGENOME_VS_NR}

.PHONY: regression_blastx_nr_vs_WB4_2_0811
regression_blastx_nr_vs_WB4_2_0811: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastx-nr-WB4_2_0811.ini ${ELB_TEST_TIMEOUT_BLASTX_WB4_2_0811_VS_NR}

.PHONY: regression_tblastn_nt_vs_viral_metagenome
regression_tblastn_nt_vs_viral_metagenome: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-tblastn-nt-viral-metagenome.ini ${ELB_TEST_TIMEOUT_TBLASTN_VIRAL_META_VS_NT}

.PHONY: regression_rpsblast_vs_amr
regression_rpsblast_vs_amr: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-rpsblast-amr.ini ${ELB_TEST_TIMEOUT_RPSBLAST_AMR}

.PHONY: regression_rpstblastn_vs_wb4_2_0811
regression_rpstblastn_vs_wb4_2_0811: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-rpstblastn-WB4_2_0811.ini ${ELB_TEST_TIMEOUT_RPSTBLASTN_WB4_2_0811}

.PHONY: regression_blastn_vs_custom_db
regression_blastn_vs_custom_db: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-custom-db.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}

.PHONY: integration_test_pdbnt_single_node
integration_test_pdbnt_single_node: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-pdbnt.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}

.PHONY: integration_test_pdbnt_multi_node_autoscale
integration_test_pdbnt_multi_node_autoscale: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-pdbnt-autoscale.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}

.PHONY: integration_test_pdbnt_local_ssd
integration_test_pdbnt_local_ssd: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-blastn-pdbnt-local-ssd.ini ${ELB_TEST_TIMEOUT_MANE_VS_PDBNT}

.PHONY: aws_integration_test_contamination_screen
aws_integration_test_contamination_screen: elastic-blast
	${VENV}/bin/blast-tuner.py \
		--db nt \
		--program blastn \
		--total-query-length 2937775295 \
		--db-source AWS
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-contam.ini ${ELB_TEST_TIMEOUT_CONTAM_SCREEN}

.PHONY: integration_test_too_many_k8s_jobs
integration_test_too_many_k8s_jobs: elastic-blast
	ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test-for-job-failure.sh share/etc/elb-blastn-pdbnt-k8s-too-many-jobs.ini 5

.PHONY: integration_test_too_many_k8s_jobs_client
integration_test_too_many_k8s_jobs_client: elastic-blast
	ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
	ELB_DISABLE_JOB_SUBMISSION_ON_THE_CLOUD=1 \
		tests/tc-bash-runner.sh tests/integration-test-for-failure-with-code.sh share/etc/elb-blastn-pdbnt-k8s-too-many-jobs.ini 1


#############################################################################
# Stress test suite: defined as tests cases that run for more than 5 hours and
# stress the components/infrastructure

# This is an archetypical test case for ElasticBLAST, runs lots of contigs of unknown taxonomy and tries to classify them.
# Stresses the query splitting module (lots of data), the submission of BLAST jobs (lots of jobs)
# Stems from EB-674, EB-737, EB-788
.PHONY: stress-test_aws_regression_rpstblastn_vs_split_cdd_five_autoscale
stress-test_aws_regression_rpstblastn_vs_split_cdd_five_autoscale: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-rpstblastn-five-example.ini ${ELB_TEST_TIMEOUT_RPSTBLASTN_FIVE}

# This is an archetypical test case for ElasticBLAST, runs lots of contigs of unknown taxonomy and tries to classify them.
# Stresses the query splitting module (lots of data), the submission of BLAST jobs (lots of jobs)
# Stems from EB-674
.PHONY: stress-test_regression_rpstblastn_vs_split_cdd_five_autoscale
stress-test_regression_rpstblastn_vs_split_cdd_five_autoscale: elastic-blast
	-ELB_GCP_PROJECT=${ELB_GCP_PROJECT} \
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-rpstblastn-five-example.ini ${ELB_TEST_TIMEOUT_RPSTBLASTN_FIVE}

# This test saturates the network bandwidth on the EBS volume. 
# Stems from EB-993
.PHONY: stress-test_aws_regression_blastp_dark_matter
stress-test_aws_regression_blastp_dark_matter: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastp-dark-matter.ini ${ELB_TEST_TIMEOUT_BLASTP_NR_DARK_MATTER}

# This test saturates the network bandwidth on the EBS volume, but it uses the AWS instance type
# Stems from EB-993
.PHONY: stress-test_aws_regression_blastp_dark_matter_optimal_instance_type
stress-test_aws_regression_blastp_dark_matter_optimal_instance_type: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastp-dark-matter-optimal-spot.ini ${ELB_TEST_TIMEOUT_BLASTP_NR_DARK_MATTER}

# This uses SSDs and thus does *not* saturate the network bandwidth as the dark-matter test
# cases above. It's provided as a means to compare runtime with the tests above
# Stems from EB-993
.PHONY: stress-test_aws_regression_blastp_nr_vs_dark_matter_ssd
stress-test_aws_regression_blastp_nr_vs_dark_matter_ssd: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastp-dark-matter-nvme.ini ${ELB_TEST_TIMEOUT_BLASTP_NR_DARK_MATTER}

# This uses SSDs and thus does *not* saturate the network bandwidth as the dark-matter test
# cases above. It's provided as a means to compare runtime with the test above
# Stems from EB-993
.PHONY: stress-test_aws_regression_blastp_nr_vs_dark_matter_ssd-4-jobs
stress-test_aws_regression_blastp_nr_vs_dark_matter_ssd-4-jobs: elastic-blast
	-ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastp-dark-matter-nvme-4-jobs.ini ${ELB_TEST_TIMEOUT_BLASTP_NR_DARK_MATTER}

# This uses a large BLASTDB (415GB), requires large instance type to keep the database in memory.
# Stems from EB-936
# Publication reference: https://www.biorxiv.org/content/10.1101/2021.02.16.431451v2
.PHONY: stress-test_aws_regression_megablast_sra_spots_vs_refseq_genomes
stress-test_aws_regression_megablast_sra_spots_vs_refseq_genomes: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-megablast-sra-spots.ini ${ELB_TEST_TIMEOUT_MEGABLAST_SRA_SPOTS_VS_REFSEQ_GENOMES}


# This is a VERY computationally intensive search. Never run to completion,
# basic linear extrapolation gives around 9 days on the environment defined in
# the configuration file.
# Stems from EB-955
.PHONY: stress-test_aws_regression_blastp_viral_metagenomes_vs_nr
stress-test_aws_regression_blastp_viral_metagenomes_vs_nr: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-viralmetagenomes-vs-nr.ini ${ELB_TEST_TIMEOUT_BLASTP_VIRAL_METAGENOME_VS_NR}

# This test saturates the network bandwidth on the EBS volume. 
# Stems from EB-1004
.PHONY: stress-test_aws_regression_blastx_jaers_wgs
stress-test_aws_regression_blastx_jaers_wgs: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastx-nr-jaers-wgs.ini ${ELB_TEST_TIMEOUT_JAERS_VS_NR}

# This uses SSDs and thus does *not* saturate the network bandwidth as the test
# case above. It's provided as a means to compare runtime with the test above
# Stems from EB-1004
.PHONY: stress-test_aws_regression_blastx_jaers_wgs_ssd
stress-test_aws_regression_blastx_jaers_wgs_ssd: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test.sh share/etc/elb-aws-blastx-nr-jaers-wgs.ini ${ELB_TEST_TIMEOUT_JAERS_VS_NR}


.PHONY: test_script_based_interface_dry_run
test_script_based_interface_dry_run: export ELB_USE_PREEMPTIBLE=1
test_script_based_interface_dry_run: export ELB_GCP_PROJECT=ncbi-sandbox-blast
test_script_based_interface_dry_run: export CLOUDSDK_CORE_PROJECT=ncbi-sandbox-blast
test_script_based_interface_dry_run: export ELB_GCP_REGION=us-east4
test_script_based_interface_dry_run: export ELB_GCP_ZONE=us-east4-a
test_script_based_interface_dry_run: elastic-blast
	./elastic-blast submit \
		--results ${ELB_RESULTS} \
		--program ${ELB_BLAST_PROGRAM} \
		--db ${ELB_DB} \
		--query ${ELB_QUERIES} \
		--num-nodes ${ELB_NUM_NODES} \
		--dry-run --logfile stderr --loglevel DEBUG \
		-- -task blastn -evalue 1e-20 -show_gis -max_target_seqs 20 -outfmt "6 qgi qacc  sgi sacc staxids slen length"
	./elastic-blast status --dry-run --results gs://user-bucket --logfile stderr --loglevel DEBUG 
	./elastic-blast delete --cfg share/etc/elb-blastn-pdbnt.ini --results gs://user-bucket --loglevel DEBUG --dry-run --logfile stderr
	./elastic-blast submit --dry-run --cfg share/etc/elb-blastn-pdbnt-autoscale.ini --results gs://user-bucket --loglevel DEBUG --logfile stderr
	-./elastic-blast run-summary --cfg share/etc/elb-blastn-pdbnt.ini --results gs://user-bucket --loglevel DEBUG --dry-run --logfile stderr
	-./elastic-blast run-summary --results ${SAMPLE_AWS_RESULTS} --loglevel DEBUG --dry-run --logfile stderr

	#./elastic-blast submit \
	#	--program ${ELB_BLAST_PROGRAM} \
	#	--db ${ELB_DB} \
	#	--query ${ELB_QUERIES} \
	#	--num-nodes ${ELB_NUM_NODES} \
	#	--dry-run --logfile stderr --loglevel DEBUG
	#./elastic-blast status --dry-run --logfile stderr --loglevel DEBUG 
.PHONY: aws_test_script_based_interface_dry_run
aws_test_script_based_interface_dry_run: elastic-blast
	./elastic-blast delete --dry-run --cfg share/etc/elb-aws-blastn-pdbnt.ini --loglevel DEBUG --logfile stderr
	./elastic-blast submit --dry-run --cfg share/etc/elb-aws-blastn-pdbnt.ini --loglevel DEBUG --logfile stderr

.PHONY: blast-tuner-smoke-test
blast-tuner-smoke-test: blast-tuner-blastn blast-tuner-blastp blast-tuner-blastx blast-tuner-tblastn blast-tuner-tblastx blast-tuner-rpsblast blast-tuner-rpstblastn blast-tuner-psiblast blast-tuner-expected-failures blast-tuner-custom-blastdb blast-tuner-bad-db-mol-type

.PHONY: aws-janitor-smoke-test
aws-janitor-smoke-test: ${VENV}
	[[ ${ELB_RESULTS} == s3* ]] || { echo "Please set ELB_RESULTS environment variable to an S3 path"; exit 1; }
	source ${VENV}/bin/activate && src/elastic_blast/janitor.py --dry-run --results ${ELB_RESULTS}

.PHONY: aws-janitor-delete-search
aws-janitor-delete-search: ${VENV}
	[[ ${ELB_RESULTS} == s3* ]] || { echo "Please set ELB_RESULTS environment variable to an S3 path"; exit 1; }
	source ${VENV}/bin/activate && src/elastic_blast/janitor.py --results ${ELB_RESULTS}

TMP_OUTPUT:=$(shell mktemp -t "run-summary-XXXXXXX.json")
.PHONY: blast-tuner-psiblast
blast-tuner-psiblast: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db swissprot --program psiblast --total-query-length 100000000 --logfile stderr --loglevel DEBUG --db-source NCBI --csp-target AWS | \
		tee ${TMP_OUTPUT}
	grep -v 'mt_mode 1' ${TMP_OUTPUT}
	${VENV}/bin/blast-tuner.py --db swissprot --program psiblast --total-query-length 100000000 --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal | \
		tee ${TMP_OUTPUT}
	grep -v 'mt_mode 1' ${TMP_OUTPUT}

.PHONY: blast-tuner-custom-blastdb
blast-tuner-custom-blastdb: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db s3://elasticblast-test/db/refseq_genomes/refseq_genomes --program blastn --total-query-length 100000000 --logfile stderr --loglevel DEBUG --db-source AWS
	${VENV}/bin/blast-tuner.py --db s3://elasticblast-test/db/refseq_genomes/refseq_genomes  --program blastn --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal

.PHONY: blast-tuner-rpsblast
blast-tuner-rpsblast: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db cdd   --program rpsblast --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS
	${VENV}/bin/blast-tuner.py --db cdd   --program rpsblast --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal

.PHONY: blast-tuner-rpstblastn
blast-tuner-rpstblastn: export ELB_GCP_PROJECT=ncbi-sandbox-blast
blast-tuner-rpstblastn: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db cdd   --program rpstblastn --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source GCP --gcp-project ${ELB_GCP_PROJECT}
	${VENV}/bin/blast-tuner.py --db cdd   --program rpstblastn --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal

.PHONY: blast-tuner-tblastn
blast-tuner-tblastn: export ELB_GCP_PROJECT=ncbi-sandbox-blast
blast-tuner-tblastn: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db nt  --program tblastn --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI --csp-target GCP --gcp-project ${ELB_GCP_PROJECT}
	${VENV}/bin/blast-tuner.py --db nt  --program tblastn --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal

.PHONY: blast-tuner-tblastx
blast-tuner-tblastx: export ELB_GCP_PROJECT=ncbi-sandbox-blast
blast-tuner-tblastx: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db nt  --program tblastx --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI --csp-target AWS
	${VENV}/bin/blast-tuner.py --db nt  --program tblastx --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal
	${VENV}/bin/blast-tuner.py --db nt  --program tblastx --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source GCP --gcp-project ${ELB_GCP_PROJECT}

.PHONY: blast-tuner-blastx
blast-tuner-blastx: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db nr   --program blastx --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI --csp-target AWS
	${VENV}/bin/blast-tuner.py --db nr   --program blastx --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal

.PHONY: blast-tuner-blastn
blast-tuner-blastn: export ELB_GCP_PROJECT=ncbi-sandbox-blast
blast-tuner-blastn: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db nt  --program blastn --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI --csp-target GCP --gcp-project ${ELB_GCP_PROJECT}
	${VENV}/bin/blast-tuner.py --db nt  --program blastn --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI --csp-target AWS
	${VENV}/bin/blast-tuner.py --db nt  --program blastn --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal

.PHONY: blast-tuner-blastp
blast-tuner-blastp: export ELB_GCP_PROJECT=ncbi-sandbox-blast
blast-tuner-blastp: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --db nr   --program blastp --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI --csp-target GCP --gcp-project ${ELB_GCP_PROJECT}
	${VENV}/bin/blast-tuner.py --db nr   --program blastp --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source AWS --with-optimal

.PHONY: blast-tuner-expected-failures
blast-tuner-expected-failures: ${VENV} bin/blast-tuner.py
	-${VENV}/bin/blast-tuner.py --db this-db-does-not-exist  --program blastn --total-query-length 1000000  --logfile stderr --loglevel DEBUG
	-${VENV}/bin/blast-tuner.py --db nr   --program blastp --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI --with-optimal
	-${VENV}/bin/blast-tuner.py --db nr   --program blastp --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI
	-${VENV}/bin/blast-tuner.py --db nr   --program blastp --total-query-length 100000000  --logfile stderr --loglevel DEBUG --db-source NCBI --region us-east4
	${VENV}/bin/blast-tuner.py --program magicblast; \
		if [ $$? -eq 0 ] ; then \
		echo "blast-tuner.py error: should exit with non-zero for unsupported program"; exit 1; \
		fi

.PHONY: blast-tuner-bad-db-mol-type
blast-tuner-bad-db-mol-type: export ELB_GCP_PROJECT=ncbi-sandbox-blast
blast-tuner-bad-db-mol-type: ${VENV} bin/blast-tuner.py
	${VENV}/bin/blast-tuner.py --program blastn --db swissprot --total-query-length 50000 --csp-target GCP --gcp-project ${ELB_GCP_PROJECT} ; \
		if [ $$? -eq 0 ] ; then \
		echo "blast-tuner.py should exit with an error for wrong database molecular type"; exit 1; \
		fi

.PHONY: out-of-memory-expected-failure
out-of-memory-expected-failure: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test-for-job-failure.sh share/etc/elb-aws-blastn-out-of-memory.ini ${ELB_TEST_TIMEOUT_OUT_OF_MEM_EXPECTED_FAILURE}

.PHONY: out-of-memory-db-download-expected-failure
out-of-memory-db-download-expected-failure: elastic-blast
	ELB_RESULTS=${ELB_RESULTS} \
		tests/tc-bash-runner.sh tests/integration-test-for-job-failure.sh share/etc/elb-aws-blastn-out-of-memory-db-download.ini ${ELB_TEST_TIMEOUT_OUT_OF_MEM_EXPECTED_FAILURE_DB}

check_k8s:
	-kubectl delete -f share/test 2>/dev/null
	-kubectl apply -f share/test
	-time kubectl wait --for=condition=complete -f share/test/job-show-blastdbs.yaml

test: check_k8s ${VENV}
	source ${VENV}/bin/activate && python3 setup.py test
	# This tests splitting FASTA into ~20,000 files and uploading it to GCP
	source ${VENV}/bin/activate && tests/fasta_split/performance-test.sh 3m

.PHONY: test_summary
test_summary: ${VENV} test_summary_aws test_summary_gcp

SAMPLE_AWS_RESULTS?=s3://elasticblast-tomcat/tc-elb-blastn-multi-query-15
.PHONY: test_summary_aws
test_summary_aws:
	source ${VENV}/bin/activate && elastic-blast run-summary --results ${SAMPLE_AWS_RESULTS} | tee ${TMP_OUTPUT} | jq -r .
	source ${VENV}/bin/activate && tests/run_summary_correctness_test.py ${TMP_OUTPUT}

SAMPLE_GCP_RESULTS?=gs://tomcat-test/tc-elb-int-test--pdbnt-autoscale-2258
.PHONY: test_summary_gcp
test_summary_gcp: export ELB_GCP_PROJECT=ncbi-sandbox-blast
test_summary_gcp: export ELB_GCP_REGION=us-east4
test_summary_gcp: export ELB_GCP_ZONE=us-east4-b
test_summary_gcp:
	#gsutil ls -r ${SAMPLE_GCP_RESULTS}
	source ${VENV}/bin/activate && elastic-blast run-summary --results ${SAMPLE_GCP_RESULTS} | tee ${TMP_OUTPUT} | jq -r .
	source ${VENV}/bin/activate && tests/run_summary_correctness_test.py ${TMP_OUTPUT}

#############################################################################
# Operational targets
get_results:
	gsutil -qm cp ${ELB_RESULTS}/*.out.gz .
	-gsutil -qm cp ${ELB_RESULTS}/metadata/* .

test_asn_results: get_results download_split_queries
	find . -name "batch*.out.gz" -type f -print0 | xargs -0 -P8 -I{} -t gzip -t {}
	find . -name "batch*.out.gz" -type f -print0 | xargs -0 -P8 -I{} -t bash -c "zcat {} | datatool -m /netopt/ncbi_tools64/c++.metastable/src/objects/blast/blast.asn -M /am/ncbiapdata/asn/asn.all -v - -e /dev/null"
	test $(shell ls -1 *fa | wc -l) -eq $(shell ls *.out.gz | wc -l)
	test $(shell du -a -b *.out.gz | sort -n | head -n 1 | cut -f 1) -gt 0

download_split_queries:
	-gsutil -qm cp ${QUERY_BATCHES}/*.fa .

clear_results:
	-gsutil -qm rm ${ELB_RESULTS}/*.out.gz
	-gsutil -qm rm ${ELB_RESULTS}/*.fa
	-gsutil -qm rm ${ELB_RESULTS}/*.out
	-gsutil -qm rm ${ELB_RESULTS}/*.asn
	-gsutil -qm rm -rf ${ELB_RESULTS}/metadata
	-gsutil -qm rm -rf ${ELB_RESULTS}/logs
	-gsutil -qm rm -rf ${ELB_RESULTS}/query_batches

clean: delete
	find . -name __pycache__ | xargs ${RM} -rf
	${RM} -r ${VENV} .eggs .mypy_cache .pytest_cache .tox htmlcov
	${RM} elastic-blast elb-cost blast-tuner iam-policy.json
	${RM} ${ELB_LOGFILE}
	${RM} elb-run-summary.json
	-gsutil -qm rm -rf ${ELB_RESULTS}/metadata
	-gsutil -qm rm -rf ${ELB_RESULTS}/logs

distclean: clear_results clean 
	(cd share/test && ${RM} *.out.gz *.fa *.fsa ${ELB_DB}.* taxdb.* *.out *.asn)

show_config:
	env | grep ^ELB | sort
	-printenv KUBECONFIG

# Replaces prepare-binaries build step
.PHONY: tc-copy-elastic-blast-dep
tc-copy-elastic-blast-dep:
	pwd
	ls -lR
	cp -v build_deps/* .
	touch .env elastic-blast*
	-ls -ltr ${PYTHON_SOURCE} ${YAML_TEMPLATES} ${VENV} elastic-blast

#############################################################################
# Release management targets
RELEASE_BUCKET?=gs://elastic-blast/release

VERSION?=$(shell ./elastic-blast --version | sed -e 's/elastic-blast //' )
.PHONY: release
release: ${VENV} elastic-blast
	. ${VENV}/bin/activate && python3 setup.py sdist
	mv dist/elb-${VERSION}.tar.gz elb-${VERSION}.tgz

# Builds PEX files via GCP Cloud Build
.PHONY: gcp-release-build
gcp-release-build:
	gcloud builds submit --config pex-cloudbuild.yaml --substitutions _VERSION=${VERSION},_PY_VERSION=${PYTHON_VERSION},_TARGET=${RELEASE_BUCKET}

# FIXME: these links don't work yet, need to fix version and probably configure it correctly
#curl -I https://artifactory.ncbi.nlm.nih.gov/artifactory/do-dev/elb/elb-0.0.2-8.tar.gz
#curl -s https://artifactory.ncbi.nlm.nih.gov/artifactory/do-dev/elb/elb-0.0.2-8.tar.gz | tar ztvf -

# FIXME: this tarball includes elb-${VERSION}/share/blast_specs/blast-batch-000.yaml, which it shuld not, do not use. It's only here for reference (for now)
.PHONY: artifactory-release
artifactory-release:
	curl -sO https://artifactory.ncbi.nlm.nih.gov/artifactory/python-local-repo/elb/${VERSION}/elb-${VERSION}.tar.gz
	tar atvf elb-${VERSION}.tar.gz

#############################################################################
# Monitoring targets
monitor:
	kubectl get pods -o wide
	-kubectl top pods --containers
	kubectl top nodes

# AWS Batch job management
job_queue?=$(shell aws cloudformation describe-stacks --stack-name ${ELB_CLUSTER_NAME} --region ${ELB_AWS_REGION} --query "Stacks[0].Outputs[?OutputKey=='JobQueueName'].OutputValue" --output text)
comp_env_name=$(shell aws cloudformation describe-stacks --stack-name ${ELB_CLUSTER_NAME} --region ${ELB_AWS_REGION} --query "Stacks[0].Outputs[?OutputKey=='ComputeEnvironmentName'].OutputValue" --output text)
job_def=$(shell aws cloudformation describe-stacks --stack-name ${ELB_CLUSTER_NAME} --region ${ELB_AWS_REGION} --query "Stacks[0].Outputs[?OutputKey=='JobDefinitionName'].OutputValue" --output text)

.PHONY: aws-monitor
aws-monitor: AWS_PAGER=''
aws-monitor:
	for s in SUBMITTED PENDING RUNNABLE STARTING RUNNING SUCCEEDED FAILED; do \
		echo "Checking $$s jobs"; \
		aws batch list-jobs --region ${ELB_AWS_REGION} --job-queue ${job_queue} --job-status $$s; \
	done

progress:
	for status in Pending Running Succeeded Failed; do \
		echo -n "$$status "; \
		echo `kubectl get pods -l app=blast --field-selector=status.phase=$$status -o name| wc -l`; \
	done

check_setup_job:
	-kubectl logs -l app=setup -c get-blastdb
	-kubectl logs -l app=setup -c import-query-batches
	-kubectl describe jobs -l app=setup

top:
	kubectl get pods -o name -l app=blast | sed 's,pod/,,' | xargs -t -I{} kubectl exec {} -c blast -- top -n1 -cb

ps:
	kubectl get pods -o name -l app=blast | sed 's,pod/,,' | xargs -t -I{} kubectl exec {} -c blast -- ps aux

ELB_GCP_LOGS_FRESHNESS?=1d
logs: init
	@if [ "${ELB_CLUSTER_NAME}" == "" ] ; then echo "ELB_CLUSTER_NAME environment variable must be defined"; exit 1; fi
	gcloud logging read --project ${ELB_GCP_PROJECT} --freshness ${ELB_GCP_LOGS_FRESHNESS} --format json "resource.type=\"k8s_container\" resource.labels.project_id=\"${ELB_GCP_PROJECT}\" resource.labels.cluster_name=\"${ELB_CLUSTER_NAME}\" resource.labels.namespace_name=\"default\" resource.labels.container_name!=\"load-blastdb-into-ram\"" | jq -r 'sort_by(.timestamp)|.[] | [.timestamp,.resource.labels.pod_name,.resource.labels.container_name,.textPayload]|@tsv'

list_resources: init
	-gcloud container clusters list
	-gcloud compute disks list
	-gcloud compute instances list

# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-interruptions.html#finding-an-interrupted-Spot-Instance
aws_list_interrupted_spot_instances: creds.sh
	aws ec2 describe-instances \
		--filters Name=instance-lifecycle,Values=spot Name=instance-state-name,Values=terminated,stopped Name=tag:billingcode,Values=elastic-blast Name=tag:Owner,Values=${USER} \
			    --query "Reservations[*].Instances[*].InstanceId"

# Lists the instances running for a given ElasticBLAST cluster
aws_list_instances:
	#-aws batch describe-compute-environments --filter Name=tag:Name,Values=${ELB_CLUSTER_NAME} --output json
	-aws ec2 describe-instances --filter Name=tag:billingcode,Values=elastic-blast Name=tag:Owner,Values=${USER} Name=tag:Name,Values=${ELB_CLUSTER_NAME} --output json | \
		jq -Mr '.Reservations[].Instances[] | { IID: .InstanceId, DNS: .PublicDnsName, Type: .InstanceType } '

aws_list_resources: export AWS_PAGER=
aws_list_resources: creds.sh
	-aws cloudformation describe-stacks --stack-name ${ELB_CLUSTER_NAME}
	-aws ec2 describe-instances --filter Name=tag:billingcode,Values=elastic-blast Name=tag:Owner,Values=${USER} --output json | jq -r '.Reservations[].Instances[] | .PublicDnsName + " " + .PublicIpAddress'
	-aws batch describe-job-queues --output json
	-aws batch describe-job-definitions --status ACTIVE --output json
	-aws batch describe-compute-environments --output json

job-ids-v2.json:
	aws s3 cp ${ELB_RESULTS}/metadata/$@ .

.PHONY: aws-describe-jobs
aws-describe-jobs: job-ids-v2.json creds.sh
	source creds.sh && aws batch describe-jobs --jobs `jq -Mr .query_splitting $<`
	source creds.sh && aws batch describe-jobs --jobs `jq -Mr .job_submission $<`
	# jq's _nwise: https://stackoverflow.com/questions/51412721/how-to-split-an-array-into-chunks-with-jq
	for i in `jq -Mrc '.search|_nwise(100)' $<`; do \
		source creds.sh && aws batch describe-jobs --jobs `echo $$i | jq -Mrc '.[]' | tr '\n' ' '`; \
	done

iam-policy-with-principal.json: iam-policy.json
	share/tools/iam-policy-patcher.py $< > $@

.PHONY: validate-iam-policy-with-principal
validate-iam-policy-with-principal: iam-policy-with-principal.json
	AWS_PAGER='' aws accessanalyzer validate-policy --no-paginate --policy-document file://$< --policy-type RESOURCE_POLICY

.PHONY: test-janitor
test-janitor: export ELB_RESULTS=s3://elasticblast-tomcat/tc-hepatitis-nt-309
test-janitor: export ELB_DRY_RUN=1
test-janitor: ${VENV}
	-bash -x docker-janitor/elastic-blast-janitor.sh
	-${VENV}/bin/python3 src/elastic_blast/janitor.py --help
	-${VENV}/bin/python3 src/elastic_blast/janitor.py --dry-run --results ${ELB_RESULTS} --loglevel DEBUG --logfile stderr

###############################################################################
# AWS ElasticBLAST suport
GET_SAML_CREDS_TOOL=/net/snowman/vol/export4/blastqa/blastsoft_dev_setup_dir/get_saml_credential.sh
# 8 hours
creds.sh: export DURATION=28800
creds.sh:
	[ -f ~/.aws/credentials ] && mv ~/.aws/credentials ~/.aws/credentials~ || true
	source setenv.sh && env -u AWS_PROFILE ${GET_SAML_CREDS_TOOL} | tee $@
	-aws sts get-caller-identity

# Use to generate an AWS credentials file for the jump account. 
# Pre-requisite, the ROLEARN and PRINCIPLEARN environment variables are set in setenv.sh
AWS_PROF=$(shell source setenv.sh && printenv ROLEARN | awk -F / '{print $$NF}')
aws-credentials: export DURATION=28800
aws-credentials:
	@source setenv.sh && env -u AWS_PROFILE ${GET_SAML_CREDS_TOOL} ${USER} | \
		sed 's/export AWS_ACCESS_KEY_ID/aws_access_key_id/;s/export AWS_SECRET_ACCESS_KEY/aws_secret_access_key/;s/export AWS_SESSION_TOKEN/aws_session_token/;s/export AWS_DEFAULT_REGION/region/;s/"//g;1a[default]' | \
		egrep -v AWS_ACCT\|AWS_CRED_TIME | tee $@
	@printf "\n[${AWS_PROF}]\n" | tee -a $@
	@echo role_arn = arn:aws:iam::414262389673:role/${AWS_PROF} | tee -a $@
	@echo source_profile = default | tee -a $@
	@grep ^region $@ | tee -a $@
	cp -pv --backup=numbered $@ ~/.aws/credentials
	@echo "export AWS_PROFILE=${AWS_PROF}"
	@echo "unset AWS_CRED_TIME AWS_ACCT AWS_SESSION_TOKEN AWS_DEFAULT_REGION AWS_SECRET_ACCESS_KEY AWS_ACCESS_KEY_ID"
	-aws --profile default sts get-caller-identity
	-aws --profile ${AWS_PROF} sts get-caller-identity


AWS_LOGIN_TOOL=/net/snowman/vol/export4/blastqa/blastsoft_dev_setup_dir/aws-login

# AWS credentials for AWS-ELASTICBLAST role
# Source the generated creds.sh file.
.PHONY: aws-login
aws-login:
	( [ -f ${HOME}/.aws_login ] && mv ${HOME}/.aws_login ${HOME}/.aws_login~ ) || true
	cp .aws_login ${HOME}
	${AWS_LOGIN_TOOL} -e elastic-blast | tee creds.sh
	@echo ""
	@echo "Source creds.sh to obtain AWS credentials"


# AWS credentials needed for pushing to AWS ECR
# If no credentials for NCBI-AWS-ELASTIC-BLAST role, it will need to be
# acquired first. The target will prompt for password twice.
# Source the generated creds.sh file.
.PHONY: aws-login-ecr
aws-login-ecr:
	if ! (aws sts get-caller-identity | grep assumed-role/NCBI-AWS-ELASTICBLAST ) ; then \
	   echo "Getting credentials for NCBI-AWS-ELASTICBLAST role"; \
	   $(MAKE) aws-login; \
	   source creds.sh; \
	   echo "Getting credentials for NCBI-AWS-ELASTICBLAST-OPERATIONS role"; \
	fi && \
	${AWS_LOGIN_TOOL} -e elastic-blast-ecr | tee creds.sh
	@echo ""
	@echo "Source creds.sh to obtain AWS credentials"


.PHONY: aws-whoami
aws-whoami:
	-aws sts get-caller-identity
	-aws --profile default sts get-caller-identity
	-aws --profile ${AWS_PROF} sts get-caller-identity

.PHONY: eks-credentials
eks-credentials:
	aws eks update-kubeconfig --region ${ELB_AWS_REGION} --name ${ELB_CLUSTER_NAME}

.PHONY: aws-limits
aws-limits: ${VENV} creds.sh
	for s in CloudFormation S3 EC2 VPC; do \
		source ${VENV}/bin/activate && source creds.sh && awslimitchecker -S $$s -u; \
		source ${VENV}/bin/activate && source creds.sh && awslimitchecker -S $$s -l; \
	done

clouseau:
	[ -d $@ ] || git clone https://github.com/cfpb/clouseau

clouseau_venv: clouseau
	[ -d $@ ] || virtualenv -p python2.7 $@
	source $@/bin/activate && pip install -r $</requirements.txt

REPO_URL=ssh://git@bitbucket.be-md.ncbi.nlm.nih.gov:9418/blast/elastic-blast.git
.PHONY: scrub-code
scrub-code: clouseau_venv
	source $</bin/activate && \
		PYTHONPATH=${PYTHONPATH}:${PWD}/clouseau clouseau/bin/clouseau -h
	source $</bin/activate && \
		PYTHONPATH=${PYTHONPATH}:${PWD}/clouseau clouseau/bin/clouseau_thin -h
	source $</bin/activate && \
		PYTHONPATH=${PYTHONPATH}:${PWD}/clouseau clouseau/bin/clouseau \
			-u ${REPO_URL} -o json \
			--patterns clouseau/clouseau/patterns/default.txt

.PHONY: results2clustername
results2clustername:
	@./bin/results2clustername.sh ${ELB_RESULTS}
