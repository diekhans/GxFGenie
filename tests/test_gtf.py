"""
GTF tests
"""
import pytest
from conftest import gxf_good_test_sets
from support import get_test_input_file, get_test_output_file, diff_results_expected, gtf_to_bed_compare, safe_test_id, get_expect_error_ids, CheckRaisesCauses
from gxfgenie import gxf_parser_factory
from gxfgenie.errors import GxfGenieFormatError, GxfGenieParseError

gtf_good_test_sets = [
    "gencode/v19",
    "gtf_good/B16.stringtie.head",
    "gtf_good/ensembl_grch37.head",
    "gtf_good/refseq.ucsc.small",
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
    ["gtf_bad/bad-end", [
        (GxfGenieParseError,
         r""".*input/gtf_bad/bad-end.gtf:3: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""Invalid `end', expected a positive integer, got `7x08.*"""),]
     ],
    ["gtf_bad/bad-phase", [
        (GxfGenieParseError,
         r""".*bad-phase\.gtf:4: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""Invalid `phase', expected `0', `1', `2', or `.', got `7'"""),]
     ],
    ["gtf_bad/bad-start", [
        (GxfGenieParseError,
         r""".*gtf_bad/bad-start\.gtf:4: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""Invalid `start', expected a positive integer, got `69z1'"""),]
     ],
    ["gtf_bad/bad-strand", [
        (GxfGenieParseError,
         r""".*gtf_bad/bad-strand\.gtf:4: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Invalid `strand', expected `\+', `-', or `\.', got `32'"""),]
     ],
    ["gtf_bad/empty-feature", [
        (GxfGenieParseError,
         r""".*gtf_bad/empty-feature.gtf:4: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Invalid `feature', value may not be empty, got `'"""),]
     ],
    ["gtf_bad/empty-seq", [
        (GxfGenieParseError,
         r""".*gtf_bad/empty-seq\.gtf:2: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""Invalid `seqname', value may not be empty or contain whitespace, got `'"""),]
     ],
    ["gtf_bad/empty-source", [
        (GxfGenieParseError,
         r""".*gtf_bad/empty-source\.gtf:2: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Invalid `source', value may not be empty, got `  '"""),]
     ],
    ["gtf_bad/long-line", [
        (GxfGenieParseError,
         r""".*gtf_bad/long-line\.gtf:3: error parsing GxF record.*"""),
        (GxfGenieFormatError,
         r"""^Wrong number of columns, expected 9, got.*"""),]
     ],
    ["gtf_bad/reversed-range", [
        (GxfGenieParseError,
         r""".*gtf_bad/reversed-range.gtf:2: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""'start' column must be less-than or equal to end, got `67093604 > 67093583'"""),]
     ],
    ["gtf_bad/short-line", [
        (GxfGenieParseError,
         r""".*gtf_bad/short-line\.gtf:4: error parsing GxF record:.*"""),
        (GxfGenieFormatError,
         r"""Wrong number of columns, expected 9, got 7:.*"""),]
     ],
]

@pytest.mark.parametrize("setname, expect_spec",
                         error_test_set,
                         ids=get_expect_error_ids(error_test_set))
def test_error(setname, expect_spec, request):
    in_gtf = get_test_input_file(request, setname + ".gtf")
    parser = gxf_parser_factory(in_gtf)
    with CheckRaisesCauses(setname, expect_spec):
        for _ in parser.parse():
            pass
