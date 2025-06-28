"""
GFF3 tests
"""
import pytest
from conftest import gxf_good_test_sets
from support import get_test_input_file, safe_test_id
from gxfgenie import gxf_parser_factory

gff3_good_test_sets = [
    "gencode/polyA",
    "gencode/pseudo",
    "gencode/v42",
]

@pytest.mark.parametrize("setname",
                         gxf_good_test_sets + gff3_good_test_sets,
                         ids=safe_test_id)
def test_good(setname, request):
    in_gff = get_test_input_file(request, setname + ".gff3")
    parser = gxf_parser_factory(in_gff)
    for rec in parser.parse():
        pass
