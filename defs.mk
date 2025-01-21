# include with
#   root=../..
#   include ${root}/defs.mk

PYTHON = poetry run python3
FLAKE8 = ${PYTHON} -m flake8
PYTEST = ${PYTHON} -m pytest

export PYTHONPATH:=${root}/lib:${PYTHONPATH}
ifeq (${PYTHONWARNINGS},)
   # set to error to find were they are coming from
   export PYTHONWARNINGS=always
endif

binDir = ${root}/bin
diff = diff -u

