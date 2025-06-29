"""
pytest config file

Copyright (c) 2024-2025, Mark Diekhans
Copyright (c) 2024-2025, The Regents of the University of California
"""
import sys
import os.path as osp
import traceback
import pytest

sys.path.insert(0, osp.abspath(".."))

# command test cases for parameterize test of good parsing, less .gff3 or .gtf
gxf_good_test_sets = [
    "gencode/set1",
    "gencode/tags",
    "gencode/v21",
    "gencode/v27.par",
]

def pytest_exception_interact(node, call, report):
    # Only print native traceback for non-AssertionError
    if report.failed and not isinstance(call.excinfo.value, (AssertionError, pytest.fail.Exception)):
        traceback.print_exception(type(call.excinfo.value),
                                  call.excinfo.value,
                                  call.excinfo.tb,
                                  file=sys.stderr)
        sys.stderr.flush()
