"""
GFF3 tests
"""
import pytest
from conftest import gxf_good_test_sets
from support import get_test_input_file
from gxfgenie import gxf_parser_factory

pytestmark = pytest.mark.skip(reason="GFF3 is not yet full implemented")

@pytest.mark.parametrize("setname", gxf_good_test_sets)
def test_good(setname, request):
    in_gff = get_test_input_file(request, setname + ".gff3")
    parser = gxf_parser_factory(in_gff)
    for rec in parser.parse():
        pass
