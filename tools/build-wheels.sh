#!/bin/bash
set -e
PYTHON_VERSIONS="cp36-cp36m cp37-cp37m cp38-cp38"

# Avoid creation of __pycache__/*.py[c|o]
export PYTHONDONTWRITEBYTECODE=1

package_name="$1"
if [[ -z "$package_name" ]]
then
    &>2 echo "Please pass package name as a first argument of this script ($0)"
    exit 1
fi

arch=$(uname -m)

# Clean-up
rm -rf /io/.tox
rm -rf /io/*.egg-info
rm -rf /io/.pytest_cache
find /io/ -noleaf -name *.py[co] -delete

echo
echo
echo "Compile wheels"
for PYTHON in ${PYTHON_VERSIONS}; do
    /opt/python/"${PYTHON}"/bin/pip install -U pip setuptools wheel
    /opt/python/"${PYTHON}"/bin/pip install -r /io/build_requirements.txt
    /opt/python/"${PYTHON}"/bin/pip wheel /io/ -w /io/dist/
    cd /io
    /opt/python/"${PYTHON}"/bin/python setup.py bdist_wheel
    /opt/python/"${PYTHON}"/bin/python setup.py clean
done

echo
echo
echo "Bundle external shared libraries into the wheels"
for whl in /io/dist/${package_name}*${arch}.whl; do
    echo "Repairing $whl..."
    auditwheel repair "$whl" -w /io/dist/
done

echo "Cleanup OS specific wheels"
rm -fv /io/dist/*-linux_*.whl

echo
echo
echo "Install packages and test"
echo "dist directory:"
ls /io/dist

for PYTHON in ${PYTHON_VERSIONS}; do
    echo
    echo -n "Test $PYTHON: $package_name "
    /opt/python/"${PYTHON}"/bin/python -c "import platform;print(platform.platform())"
    /opt/python/"${PYTHON}"/bin/pip install "$package_name" --no-index -f file:///io/dist
    /opt/python/"${PYTHON}"/bin/pip install pytest
    /opt/python/"${PYTHON}"/bin/py.test -vvv /io/test
done

find /io/dist/ -noleaf -type f -not -name "*$package_name*" -delete
rm -rf /io/.eggs
rm -rf /io/build
rm -rf /io/*.egg-info
rm -rf /io/.pytest_cache
rm -rf /io/.tox
rm -f /io/.coverage
# Clean caches and cythonized
find /io/ -noleaf -name *.py[co] -delete
find /io/ -noleaf -name *.c -delete
# Reset permissions
chmod -v a+rwx /io/dist
chmod -v a+rw /io/dist/*
chmod -vR a+rw /io/"$package_name"
