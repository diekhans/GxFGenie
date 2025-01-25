"""
Various functions to support testing

Copyright (c) 2024-2025, Mark Diekhans
Copyright (c) 2024-2025, The Regents of the University of California
"""
import pytest
import sys
import os
import os.path as osp
import difflib

def get_test_id(request):
    return osp.basename(request.node.nodeid)

def get_test_dir(request):
    """Find test directory, which is were the current test_* file is at"""
    return os.path.dirname(str(request.node.fspath))

def get_test_input_file(request, fname):
    """Get a path to a file in the test input directory"""
    return osp.join(get_test_dir(request), "input", fname)

def get_test_output_dir(request):
    """get the path to the output directory to use for this test, create if it doesn't exist"""
    outdir = osp.join(get_test_dir(request), "output")
    os.makedirs(outdir, exist_ok=True)
    return outdir

def get_test_output_file(request, ext=""):
    """Get path to the output file, using the current test id and append ext,
    which should contain a dot."""
    return osp.join(get_test_output_dir(request), get_test_id(request) + ext)

def get_test_expect_file(request, ext="", *, basename=None):
    """Get path to the expected file, using the current test id and append
    ext. If basename is used, it is instead of the test id, allowing share an
    expected file between multiple tests."""
    fname = basename if basename is not None else get_test_id(request)
    return osp.join("expected", fname + ext)

def _get_lines(fname):
    with open(fname) as fh:
        return fh.readlines()

def diff_test_files(exp_file, out_file):
    """diff expected and output files."""

    exp_lines = _get_lines(exp_file)
    out_lines = _get_lines(out_file)

    diffs = list(difflib.unified_diff(exp_lines, out_lines, exp_file, out_file))
    for diff in diffs:
        print(diff, end=' ', file=sys.stderr)

    if len(diffs) > 0:
        pytest.fail(f"test output differed  expected: '{exp_file}', got: '${out_file}'")

def diff_results_expected(request, ext="", *, basename=None):
    """diff expected and output files, with names computed from test id."""
    diff_test_files(get_test_expect_file(request, ext, basename=basename),
                    get_test_output_file(request, ext))


class UncheckedType:
    "singleton to flag expected field to not check"
    def __repr__(self):
        return "<NOCHECK>"

    def __str__(self):
        return "<NOCHECK>"


NOCHECK = UncheckedType()
