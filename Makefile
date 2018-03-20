.PHONY: test sdist bdist_wheel_linux bdist_windows

clean:
	python setup.py clean

fresh_toolchain:
	python -m pip install -U pip setuptools

check_docs: fresh_toolchain
	pip install -U collective.checkdocs
	python setup.py checkdocs

test:
	tox

sdist: clean fresh_toolchain check_docs
	python setup.py sdist --formats zip

bdist_wheel_linux: clean
	./tools/run_docker.sh "threaded"

bdist_rpm: clean fresh_toolchain check_docs
	@FPM=$$(find /usr/bin /usr/local/bin ~/.gem -name fpm -executable -type f -print -quit);\
	echo "Use FPM in $$FPM";\
	$$FPM -s python -t rpm  --python-pip pip .

bdist_deb: clean fresh_toolchain check_docs
	@FPM=$$(find /usr/bin /usr/local/bin ~/.gem -name fpm -executable -type f -print -quit);\
	echo "Use FPM in $$FPM";\
	$$FPM -s python -t deb --python-pip pip .

bdist_windows: clean fresh_toolchain check_docs
	pip install wheel==0.26
	pip install -U -r build_requirements.txt
	python setup.py bdist_wheel bdist_wininst

ALL: clean test
