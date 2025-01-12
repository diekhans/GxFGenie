root = .
include ${root}/defs.mk

src_dirs = gxfgenie tests

all:

test:
	cd tests && ${MAKE} test

lint:
	${FLAKE8} --color=never ${src_dirs}

clean:
	cd tests && ${MAKE} clean
	rm -rf ${src_dirs:%=%/__pycache__}

realclean: clean
	rm -rf .venv

savebak:
	savebak -r ${hgwdev} -git GxFGenie
