"""
GFF3 tests
"""
import pytest
from conftest import gxf_good_test_sets
from support import (get_test_input_file, get_test_output_file, diff_results_expected, gff3_to_bed_compare, safe_test_id, get_expect_error_ids,
                     CheckRaisesCauses, gff3_ucsc_validate)
from gxfgenie import gxf_parser_factory
from gxfgenie.errors import GxfGenieFormatError, GxfGenieParseError

gff3_good_test_sets = [
    "gencode/polyA",
    "gencode/pseudo",
    "gencode/v42",
    "gff3_good/discontinuous",
    "gff3_good/frameShifts",
    "gff3_good/geneMRna",
    "gff3_good/geneTranscript",
    "gff3_good/hprc",
    "gff3_good/mm10Gencode",
    "gff3_good/ncbiProblems",
    "gff3_good/ncbiRefSeq.pseudoGenes",
    "gff3_good/ncbiSegments",
    "gff3_good/noExons",
    "gff3_good/noGeneMRna",
    "gff3_good/noId",
    "gff3_good/transcriptCdsParent",
    "gff3_good/transcriptOnly",
]

_skip_gff3ToGenePred_check = frozenset((
    "gff3_good/ncbiProblems",
))

@pytest.mark.parametrize("setname",
                         gxf_good_test_sets + gff3_good_test_sets,
                         ids=safe_test_id)
def test_good(setname, request):
    in_gff3 = get_test_input_file(request, setname + ".gff3")
    out_gff3 = get_test_output_file(request, ".gff3")
    parser = gxf_parser_factory(in_gff3)
    with open(out_gff3, 'w') as fh:
        for rec in parser.parse():
            print(str(rec), file=fh)
    diff_results_expected(request, ".gff3")
    gff3_to_bed_compare(request, in_gff3, out_gff3)
    if setname not in _skip_gff3ToGenePred_check:
        gff3_ucsc_validate(request, out_gff3)


error_test_set = [
    ["gff3_bad/bogusQuotes", [
        (GxfGenieParseError,
         r""".*gff3_bad/bogusQuotes\.gff3:2: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Can't parse attribute=value: `Name='"""),]
     ],
    ["gff3_bad/errCases1", [
        (GxfGenieParseError,
         r""".*gff3_bad/errCases1\.gff3:5: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Can't parse attribute=value: `Acc:KIBRLG]"""),]
     ],
]

@pytest.mark.parametrize("setname, expect_spec",
                         error_test_set,
                         ids=get_expect_error_ids(error_test_set))
def test_error(setname, expect_spec, request):
    in_gff3 = get_test_input_file(request, setname + ".gff3")
    parser = gxf_parser_factory(in_gff3)
    with CheckRaisesCauses(setname, expect_spec):
        for _ in parser.parse():
            pass
