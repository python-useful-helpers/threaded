#!/bin/bash
set -e
PYTHON_VERSIONS="cp36-cp36m cp37-cp37m cp38-cp38 cp39-cp39"

# Avoid creation of __pycache__/*.py[c|o]
export PYTHONDONTWRITEBYTECODE=1

package_name="$1"
if [[ -z "$package_name" ]]; then
  # shellcheck disable=SC2210
  echo &>2 "Please pass package name as a first argument of this script ($0)"
  exit 1
fi

arch=$(uname -m)

# Clean-up
rm -rf /io/.tox
rm -rf /io/*.egg-info
rm -rf /io/.pytest_cache
rm -fv /io/dist/*-linux_*.whl
find /io/ -noleaf -name "*.py[co]" -delete

echo
echo
echo "Compile wheels"
cd /io

for PYTHON in ${PYTHON_VERSIONS}; do
  echo "Python ${PYTHON} ${arch}:"
  python_bin="/opt/python/${PYTHON}/bin"
  "$python_bin/pip" install -U pip setuptools auditwheel
  "$python_bin/pip" install -r /io/build_requirements.txt
  "$python_bin/pip" wheel /io/ -w /io/dist/
  "$python_bin/python" setup.py bdist_wheel clean

  wheels=(/io/dist/"${package_name}"*"${PYTHON}"*linux_"${arch}".whl)
  for whl in "${wheels[@]}"; do
    echo "Repairing $whl..."
    "$python_bin/python" -m auditwheel repair "$whl" -w /io/dist/
    echo "Cleanup OS specific wheels"
    rm -fv "$whl"
  done
  echo
done

echo
echo "Cleanup OS specific wheels"
rm -fv /io/dist/*-linux_*.whl

echo
echo
echo "Install packages and test"
echo "dist directory:"
ls /io/dist
echo

for PYTHON in ${PYTHON_VERSIONS}; do
  echo -n "Test $PYTHON ${arch}: $package_name "
  python_bin="/opt/python/${PYTHON}/bin"
  "$python_bin/python" -c "import platform;print(platform.platform())"
  "$python_bin/pip" install "$package_name" --no-index -f file:///io/dist
  "$python_bin/pip" install -r /io/pytest_requirements.txt
  "$python_bin/py.test" -vvv /io/test
  echo
done

find /io/dist/ -noleaf -type f -not -name "*$package_name*" -delete
rm -rf /io/.eggs
rm -rf /io/build
rm -rf /io/*.egg-info
rm -rf /io/.pytest_cache
rm -rf /io/.tox
rm -f /io/.coverage
# Clean caches and cythonized
find /io/ -noleaf -name "*.py[co]" -delete
find /io/ -noleaf -name "*.c" -delete
# Reset permissions
chmod -v a+rwx /io/dist
chmod -v a+rw /io/dist/*
chmod -vR a+rw /io/"$package_name"
