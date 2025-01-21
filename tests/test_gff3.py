"""
GFF3 tests
"""
import pytest
from conftest import gxf_good_test_sets
from support import get_test_input_file
from gxfgenie import gxf_parser_factory

@pytest.mark.parametrize("setname", gxf_good_test_sets)
def test_good(setname, request):
    in_gxf = get_test_input_file(request, setname + ".gff3")
    parser = gxf_parser_factory(in_gxf)
    for rec in parser:
        pass
