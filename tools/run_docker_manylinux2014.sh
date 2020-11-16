#!/bin/bash
package_name="$1"
arch="$2"
if [ -z "$package_name" ]
then
  # shellcheck disable=SC2210
  &>2 echo "Please pass package name as a first argument of this script ($0)"
  exit 1
fi
if [ -z "$arch" ]
then
  # shellcheck disable=SC2210
  &>2 echo "Please pass package architecture as a second argument of this script ($0)"
  exit 1
fi

manylinux1_image_prefix="quay.io/pypa/manylinux2014_"
dock_ext_args=""

docker pull "${manylinux1_image_prefix}${arch}" &
declare docker_pull_pid=$!

echo
echo
echo "waiting for docker pull pid $docker_pull_pid to complete downloading container for $arch arch..."
wait $docker_pull_pid  # await for docker image for current arch to be pulled from hub

echo "Building wheel for $arch arch"
[ "$arch" == "i686" ] && dock_ext_args="linux32"
docker run --rm -v "$(pwd)":/io "${manylinux1_image_prefix}${arch}" $dock_ext_args /io/tools/build-wheels.sh "$package_name"

dock_ext_args=""  # Reset docker args, just in case
