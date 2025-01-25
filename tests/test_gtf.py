"""
GTF tests
"""
import pytest
from conftest import gxf_good_test_sets
from support import get_test_input_file, get_test_output_file, diff_results_expected
from gxfgenie import gxf_parser_factory

@pytest.mark.parametrize("setname",
                         gxf_good_test_sets + ["gencode/v19"],
                         ids=lambda sn: sn.replace('/', '_'))
def test_good(setname, request):
    in_gxf = get_test_input_file(request, setname + ".gtf")
    out_gtf = get_test_output_file(request, ".gtf")
    parser = gxf_parser_factory(in_gxf)
    with open(out_gtf, 'w') as fh:
        for rec in parser:
            print(str(rec), file=fh)
    diff_results_expected(request, ".gtf")
