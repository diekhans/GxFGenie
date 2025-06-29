# Additional validation

If gffread is installed, it will be used to do additional validation of
GFF3/GTF files that are create.

If the UCSC browser tool gff3ToGenePred is installed, it will be used to do
additional validation of GFF3 files that are create.


# Test files source:
- gencode
  various files from GENCODE, used to test UCSC browser GENCODE import code 
- gtf_good
  from https://github.com/openvax/gtfparse
- gtf_bad
  manually created from other cases
- gff3_good
  from browser gff3ToGenePred tests
- gff3_bad
  from browser gff3ToGenePred tests
  some of these test relations of records, not parser
