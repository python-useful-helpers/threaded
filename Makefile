.PHONY: test sdist bdist_egg_linux bdist_windows
test:
	tox
sdist:
	python setup.py sdist -formats zip
bdist_egg_linux:
	./tools/run_docker.sh "threaded"
bdist_rpm:
	`find /usr/bin /usr/local/bin ~/.gem -name fpm -executable -type f -print -quit` -s python -t rpm .
bdist_deb:
	`find /usr/bin /usr/local/bin ~/.gem -name fpm -executable -type f -print -quit` -s python -t deb .
bdist_windows:
	python -m pip install -U pip setuptools
	pip install wheel==0.26
	pip install -U -r build_requirements.txt
	python setup.py bdist_wheel
ALL: test
