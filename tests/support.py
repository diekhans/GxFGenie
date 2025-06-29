"""
Various functions to support testing

Copyright (c) 2024-2025, Mark Diekhans
Copyright (c) 2024-2025, The Regents of the University of California
"""
import sys
import os
import os.path as osp
import re
import shutil
import difflib
import subprocess
import pytest

def safe_test_id(in_id):
    """clean up a test id so it can be used as a file name on output
    by changing `/' to `_'"""
    return in_id.replace('/', '_')

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

def _normalize_floats(line, digits=2):
    return re.sub(r'\d+\.\d+', lambda m: f"{float(m.group()):.{digits}f}", line)

def _get_lines(fname):
    with open(fname) as fh:
        return [_normalize_floats(line) for line in fh]

def diff_test_files(exp_file, out_file):
    """diff expected and output files."""

    exp_lines = _get_lines(exp_file)
    out_lines = _get_lines(out_file)

    diffs = list(difflib.unified_diff(exp_lines, out_lines, exp_file, out_file))
    for diff in diffs:
        print(diff, end=' ', flush=True, file=sys.stderr)

    if len(diffs) > 0:
        pytest.fail(f"test output differed,  expected: '{exp_file}', got: '${out_file}'")

def diff_results_expected(request, ext="", *, basename=None):
    """diff expected and output files, with names computed from test id."""
    diff_test_files(get_test_expect_file(request, ext, basename=basename),
                    get_test_output_file(request, ext))

def _mk_err_spec(re_part, const_part):
    """Generate an exception matching regexp with a re part and an escaped static part
    This is manually used to generate error_sets.  Uses while developing tests."""
    pass

def _print_err_spec(setname, expect_spec, got_chain):
    """print out to use to manually edit test expected data"""
    print('@>', setname, flush=True, file=sys.stderr)
    for got in got_chain:
        print(f"  {got[0].__name__}", repr(got[1]), flush=True, file=sys.stderr)

class CheckRaisesCauses:
    """
    Validate exception chain against  [(exception, regex), ...].
    """
    def __init__(self, setname, expect_spec):
        self.setname = setname
        self.expect_spec = expect_spec

    def __enter__(self):
        return self

    @staticmethod
    def _build_got_chain(exc):
        "convert exception chain to a list to match"
        got = []
        while exc is not None:
            got.append((type(exc), str(exc)))
            exc = getattr(exc, "__cause__", None)
        return got

    @staticmethod
    def _check_except(got, expect):
        if got[0] != expect[0]:
            raise AssertionError(f"Expected exception of type `{expect[0].__name__}', got '{got[0].__name__}'")
        if not re.search(expect[1], got[1]):
            raise AssertionError(f"Expected message matching `{expect[1]}', got `{got[1]}'")

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Checks the raised exception and its causes against the provided list.
        """
        if exc_type is None:
            raise AssertionError("No exception was raised")
        got_chain = self._build_got_chain(exc_value)

        try:
            # check values before checking length to be easier to debug
            for got, expect in zip(got_chain, self.expect_spec):
                self._check_except(got, expect)

            if len(self.expect_spec) != len(got_chain):
                raise AssertionError(f"Expect exception cause chain of {len(self.expect_spec)}, got {len(got_chain)}: {got_chain}")
        except Exception:
            # this makes debugging easier
            _print_err_spec(self.setname, self.expect_spec, got_chain)
            raise

        return True


# cache of program check results
_exp_program_check_cache = {}

def _have_ext_program(prog):
    found = _exp_program_check_cache.get(prog)
    if found is None:
        found = shutil.which(prog) is not None
        _exp_program_check_cache[prog] = found
        if not found:
            print(f"Note: {prog} program is not found, some extra test validations", flush=True, file=sys.stderr)
    return found

def _have_gffread():
    return _have_ext_program("gffread")

def _bed_to_gxf(request, gxf, is_gtf, typedir):
    outdir = get_test_output_dir(request)
    subdir = "gtf_bed" if is_gtf else "gff3_bed"
    bed = osp.join(outdir, subdir, typedir, get_test_id(request) + ".bed")
    os.makedirs(osp.dirname(bed), exist_ok=True)
    subprocess.check_call(["gffread", "--bed", gxf, "-o", bed])
    return bed

def _gxf_to_bed_compare(request, in_gxf, out_gxf, *, is_gtf=False):
    expect_bed = _bed_to_gxf(request, in_gxf, is_gtf, 'expect')
    got_bed = _bed_to_gxf(request, out_gxf, is_gtf, 'got')
    diff_test_files(expect_bed, got_bed)

def gtf_to_bed_compare(request, in_gtf, out_gtf):
    """compare GTF output with source by converting to bed, if gffread is
    available"""
    if _have_gffread():
        _gxf_to_bed_compare(request, in_gtf, out_gtf, is_gtf=True)

def gff3_to_bed_compare(request, in_gff3, out_gff3):
    """compare GFF3 output with source by converting to bed, if gffread is
    available"""
    if _have_gffread():
        _gxf_to_bed_compare(request, in_gff3, out_gff3)

def _have_gff3ToGenePred():
    return _have_ext_program("gff3ToGenePred")

def gff3_ucsc_validate(request, out_gff3):
    """validate GFF3 with UCSC browser's program"""
    if _have_gff3ToGenePred():
        # discard stderr if warnings
        results = subprocess.run(["gff3ToGenePred", out_gff3, "/dev/null"], stderr=subprocess.PIPE, text=True)
        if results.returncode != 0:
            pytest.fail(f"gff3ToGenePred failed on `{out_gff3}':\n{results.stderr}")

def get_expect_error_ids(expect_spec):
    """error id based on input file name in a list where each expect_spec[*][0]
    is the relative file name"""
    return [osp.basename(r[0]) for r in expect_spec]
