root = ..
include ${root}/defs.mk

# run a limited number of tests
#   make libtests tests=test_analyze.py
#   make libtests tests=test_analyze.py::test_analysis_fred
tests = .

# override number of process with nproc=1, etc
# stdout not echo with mulitple processed
nproc = 20

# debug=--debug
debug = 

# override with pytest_extra=-v or what ever
pytest_extra = 

# to get less verbose traceback
traceback = --tb=native

# used to find source of ResourceWarning
# export PYTHONTRACEMALLOC = 20

test:
	${PYTEST} ${traceback} -n ${nproc} ${pytest_extra} ${tests}

mkdirs:
	@mkdir -p output

savebak:
	cd .. && ${MAKE} savebak

lint:
	cd .. && ${MAKE} lint

clean:
	rm -rf output __pycache__

