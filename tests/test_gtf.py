"""
GTF tests
"""
import pytest
import os.path as osp
from conftest import gxf_good_test_sets
from support import get_test_input_file, get_test_output_file, diff_results_expected, gtf_to_bed_compare, safe_test_id, CheckRaisesCauses
from gxfgenie import gxf_parser_factory
from gxfgenie.errors import GxfGenieFormatError, GxfGenieParseError

gtf_goot_test_sets = [
    "gencode/v19",
    "misc/B16.stringtie.head",
    "misc/ensembl_grch37.head",
    "misc/refseq.ucsc.small",
]

@pytest.mark.parametrize("setname",
                         gxf_good_test_sets + gtf_goot_test_sets,
                         ids=safe_test_id)
def test_good(setname, request):
    in_gtf = get_test_input_file(request, setname + ".gtf")
    out_gtf = get_test_output_file(request, ".gtf")
    parser = gxf_parser_factory(in_gtf)
    with open(out_gtf, 'w') as fh:
        for rec in parser.parse():
            print(str(rec), file=fh)
    diff_results_expected(request, ".gtf")
    gtf_to_bed_compare(request, in_gtf, out_gtf)


error_test_set = [
    ["errors/bad-end", [
        (GxfGenieParseError,
         """bad-end1"""),
        (GxfGenieFormatError,
         """bad-end21"""),]
     ],
    ["errors/bad-phase", [
        (GxfGenieParseError,
         """bad-phase1"""),
        (GxfGenieFormatError,
         """bad-phase2"""),]
     ],
    ["errors/bad-start", [
        (GxfGenieParseError,
         """bad-start1"""),
        (GxfGenieFormatError,
         """bad-start2"""),]
     ],
    ["errors/bad-strand", [
        (GxfGenieParseError,
         """bad-strand1"""),]],
    ["errors/empty-feature", [
        (GxfGenieParseError,
         """empty-feature"""),]],
    ["errors/empty-seq", [
        (GxfGenieParseError,
         """empty-seq"""),]],
    ["errors/empty-source", [
        (GxfGenieParseError,
         """empty-source"""),]],
    ["errors/long-line", [
        (GxfGenieParseError,
         """long-line"""),]],
    ["errors/reversed-range", [
        (GxfGenieParseError,
         """reversed-range"""),]],
    ["errors/short-line", [
        (GxfGenieParseError,
         """short-line"""),]],
]

F@> errors/bad-phase
  GxfGenieParseError 'Error: /Users/markd/compbio/code/GxFGenie/tests/input/errors/bad-phase.gtf:4: error parsing GxF record: `chr1\tHAVANA\tCDS\t69091\t70005\t.\t+\t7\tgene_id "ENSG00000186092.4"; transcript_id "ENST00000335137.3"; gene_type "protein_coding"; gene_status "KNOWN"; gene_name "OR4F5"; transcript_type "protein_coding"; transcript_status "KNOWN"; transcript_name "OR4F5-001"; exon_number 1; exon_id "ENSE00002319515.1"; level 2; protein_id "ENSP00000334393.3"; tag "basic"; transcript_support_level "NA"; tag "appris_principal"; tag "CCDS"; ccdsid "CCDS30547.1"; havana_gene "OTTHUMG00000001094.1"; havana_transcript "OTTHUMT00000003223.1";\''
  GxfGenieFormatError "Invalid `phase', expected `0', `1', `2', or `.', got `7'"
F@> errors/bad-start
  GxfGenieParseError 'Error: /Users/markd/compbio/code/GxFGenie/tests/input/errors/bad-start.gtf:4: error parsing GxF record: `chr1\tHAVANA\tCDS\t69z1\t70005\t.\t+\t0\tgene_id "ENSG00000186092.4"; transcript_id "ENST00000335137.3"; gene_type "protein_coding"; gene_status "KNOWN"; gene_name "OR4F5"; transcript_type "protein_coding"; transcript_status "KNOWN"; transcript_name "OR4F5-001"; exon_number 1; exon_id "ENSE00002319515.1"; level 2; protein_id "ENSP00000334393.3"; tag "basic"; transcript_support_level "NA"; tag "appris_principal"; tag "CCDS"; ccdsid "CCDS30547.1"; havana_gene "OTTHUMG00000001094.1"; havana_transcript "OTTHUMT00000003223.1";\''
  GxfGenieFormatError "Invalid `start', expected a positive integer, got `69z1'"
F@> errors/bad-strand
  GxfGenieParseError 'Error: /Users/markd/compbio/code/GxFGenie/tests/input/errors/bad-strand.gtf:4: error parsing GxF record: `chr1\tHAVANA\tCDS\t69091\t70005\t.\t32\t0\tgene_id "ENSG00000186092.4"; transcript_id "ENST00000335137.3"; gene_type "protein_coding"; gene_status "KNOWN"; gene_name "OR4F5"; transcript_type "protein_coding"; transcript_status "KNOWN"; transcript_name "OR4F5-001"; exon_number 1; exon_id "ENSE00002319515.1"; level 2; protein_id "ENSP00000334393.3"; tag "basic"; transcript_support_level "NA"; tag "appris_principal"; tag "CCDS"; ccdsid "CCDS30547.1"; havana_gene "OTTHUMG00000001094.1"; havana_transcript "OTTHUMT00000003223.1";\''
  GxfGenieFormatError "Invalid `strand', expected `+', `-', or `.', got `32'"
FFFF@> errors/long-line
  GxfGenieParseError 'Error: /Users/markd/compbio/code/GxFGenie/tests/input/errors/long-line.gtf:3: error parsing GxF record: `chr1\tHAVANA\texon\t69091\t70008\t.\t+\t.\tgene_id "ENSG00000186092.4"; transcript_id "ENST00000335137.3"; gene_type "protein_coding"; gene_status "KNOWN"; gene_name "OR4F5"; transcript_type "protein_coding"; transcript_status "KNOWN"; transcript_name "OR4F5-001"; exon_number 1; exon_id "ENSE00002319515.1"; level 2; protein_id "ENSP00000334393.3"; tag "basic"; transcript_support_level "NA"; tag "appris_principal"; tag "CCDS"; ccdsid "CCDS30547.1"; havana_gene "OTTHUMG00000001094.1"; havana_transcript "OTTHUMT00000003223.1";\tchr1\tHAVANA\tgene\t69091\t70008\''
  GxfGenieFormatError 'Wrong number of columns, expected 9, got 14: `chr1\tHAVANA\texon\t69091\t70008\t.\t+\t.\tgene_id "ENSG00000186092.4"; transcript_id "ENST00000335137.3"; gene_type "protein_coding"; gene_status "KNOWN"; gene_name "OR4F5"; transcript_type "protein_coding"; transcript_status "KNOWN"; transcript_name "OR4F5-001"; exon_number 1; exon_id "ENSE00002319515.1"; level 2; protein_id "ENSP00000334393.3"; tag "basic"; transcript_support_level "NA"; tag "appris_principal"; tag "CCDS"; ccdsid "CCDS30547.1"; havana_gene "OTTHUMG00000001094.1"; havana_transcript "OTTHUMT00000003223.1";\tchr1\tHAVANA\tgene\t69091\t70008\''
F@> errors/reversed-range
  GxfGenieParseError "Error: /Users/markd/compbio/code/GxFGenie/tests/input/errors/reversed-range.gtf:1: error parsing GxF record: `chr10\tHAVANA\tgene\t45315608\t45302298\t.\t-\t.\tID=ENSG00000256574.8;gene_id=ENSG00000256574.8;gene_type=protein_coding;gene_name=OR13A1;level=2;hgnc_id=HGNC:14772;havana_gene=OTTHUMG00000018080.4'"
  GxfGenieFormatError "Can't parse attribute/value: `ID=ENSG00000256574.8'"
F@> errors/short-line
  GxfGenieParseError "Error: /Users/markd/compbio/code/GxFGenie/tests/input/errors/short-line.gtf:4: error parsing GxF record: `chr1\tHAVANA\tCDS\t69091\t70005\t.\t+'"
  GxfGenieFormatError "Wrong number of columns, expected 9, got 7: `chr1\tHAVANA\tCDS\t69091\t70005\t.\t+'"


def error_ids(expect_spec):
    "error id based on input file name"
    return [osp.basename(r[0]) for r in expect_spec]

@pytest.mark.parametrize("setname, expect_spec",
                         error_test_set,
                         ids=error_ids(error_test_set))
def test_error(setname, expect_spec, request):
    in_gtf = get_test_input_file(request, setname + ".gtf")
    parser = gxf_parser_factory(in_gtf)
    with CheckRaisesCauses(setname, expect_spec):
        for rec in parser.parse():
            pass
