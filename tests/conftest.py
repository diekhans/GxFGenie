"""
pytest config file

Copyright (c) 2024-2025, Mark Diekhans
Copyright (c) 2024-2025, The Regents of the University of California
"""
import sys
import os.path as osp

sys.path.insert(0, osp.abspath(".."))

# command test cases for parameterize test of good parsing, less .gff3 or .gtf
gxf_good_test_sets = [
    "gencode/set1",
    "gencode/tags",
    "gencode/v21",
    "gencode/v27.par",
]
