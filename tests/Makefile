root = ..
include ${root}/defs.mk

# run a limited number of tests
#   make libtests tests=test_analyze.py
#   make libtests tests=test_analyze.py::test_analysis_fred
tests = .

# override number of process with nproc=0 to run
# in main process.
# stdout not echo with mulitple processes
nproc = 20

# debug=--debug
debug = 

# override with pytest_extra=-v or what ever
pytest_extra = 

# conftest.py generates a full native traceback for non-assert errors
traceback = --tb=short

# used to find source of ResourceWarning
# export PYTHONTRACEMALLOC = 20

test:
	${PYTEST} ${traceback} --numprocesses=${nproc} ${pytest_extra} ${tests}

mkdirs:
	@mkdir -p output

savebak:
	cd .. && ${MAKE} savebak

lint:
	cd .. && ${MAKE} lint

clean:
	rm -rf output __pycache__

