"""
GTF tests
"""
import pytest
import os.path as osp
from conftest import gxf_good_test_sets
from support import get_test_input_file, get_test_output_file, diff_results_expected, gtf_to_bed_compare, safe_test_id, CheckRaisesCauses
from gxfgenie import gxf_parser_factory
from gxfgenie.errors import GxfGenieFormatError, GxfGenieParseError

gtf_good_test_sets = [
    "gencode/v19",
    "misc/B16.stringtie.head",
    "misc/ensembl_grch37.head",
    "misc/refseq.ucsc.small",
]

@pytest.mark.parametrize("setname",
                         gxf_good_test_sets + gtf_good_test_sets,
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
         r""".*input/errors/bad-end.gtf:3: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""Invalid `end', expected a positive integer, got `7x08.*"""),]
     ],
    ["errors/bad-phase", [
        (GxfGenieParseError,
         r""".*bad-phase\.gtf:4: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""Invalid `phase', expected `0', `1', `2', or `.', got `7'"""),]
     ],
    ["errors/bad-start", [
        (GxfGenieParseError,
         r""".*errors/bad-start\.gtf:4: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""Invalid `start', expected a positive integer, got `69z1'"""),]
     ],
    ["errors/bad-strand", [
        (GxfGenieParseError,
         r""".*errors/bad-strand\.gtf:4: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Invalid `strand', expected `\+', `-', or `\.', got `32'"""),]
     ],
    ["errors/empty-feature", [
        (GxfGenieParseError,
         r""".*errors/empty-feature.gtf:4: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Invalid `feature', value may not be empty or contain whitespace, got `'"""),]
     ],
    ["errors/empty-seq", [
        (GxfGenieParseError,
         r""".*errors/empty-seq\.gtf:2: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""Invalid `seqname', value may not be empty or contain whitespace, got `'"""),]
     ],
    ["errors/empty-source", [
        (GxfGenieParseError,
         r""".*errors/empty-source.gtf:2: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Invalid `source', value may not be empty or contain whitespace, got `  '"""),]
     ],
    ["errors/long-line", [
        (GxfGenieParseError,
         r""".*errors/long-line\.gtf:3: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""^Wrong number of columns, expected 9, got.*"""),]
     ],
    ["errors/reversed-range", [
        (GxfGenieParseError,
         r""".*errors/reversed-range.gtf:2: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""'start' column must be less-than or equal to end, got `67093604 > 67093583'"""),]
     ],
    ["errors/short-line", [
        (GxfGenieParseError,
         r""".*errors/short-line\.gtf:4: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Wrong number of columns, expected 9, got 7:.*"""),]
     ],
]

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
        for _ in parser.parse():
            pass
