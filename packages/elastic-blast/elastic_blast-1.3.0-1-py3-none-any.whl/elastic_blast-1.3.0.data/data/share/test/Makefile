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

# Makefile with a few targets specific to tests


ELB_RESULTS ?= gs://${USER}-test
QUERY_BATCHES ?= ${ELB_RESULTS}/query_batches

# BLAST results will be downloaded to this directory from GS
DOWNLOADED_RESULTS ?= gcp_results
DOWNLOADED_QUERY_BATCHES ?= batches


get_results:
	if [ ! -d "${DOWNLOADED_RESULTS}" ]; then mkdir -p  ${DOWNLOADED_RESULTS}; fi
	gsutil -qm cp ${ELB_RESULTS}/*.out.gz ${DOWNLOADED_RESULTS}

get_split_queries:
	if [ ! -d "${DOWNLOADED_QUERY_BATCHES}" ]; then mkdir -p  ${DOWNLOADED_QUERY_BATCHES}; fi
	gsutil -qm cp ${QUERY_BATCHES}/batch_*.fa  ${DOWNLOADED_QUERY_BATCHES}


clean:
	${RM} ../blast_specs/*.yaml ../specs/*.yaml *.fa
	make -C ../split clean
	find .. -name __pycache__ | xargs ${RM} -fr

clear_results:
	make -C .. clear_results

distclean: clear_results clean 
	${RM} -R -f ${DOWNLOADED_RESULTS}
	${RM} -R -f ${DOWNLOADED_QUERY_BATCHES}
	${RM} -R -f LOCAL_BLASTDB
	${RM} -R -f local_results
	${RM} -R -f test_queries
	${RM} *.out.gz *.fa *.fsa taxdb.*


.PHONY: get_results get_split_queries clean clear_results distclean
