#!/usr/bin/env bash
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright Clairvoyant 2019
#
print_usage() {
  echo "Usage:  $1 --airflow <version> --python <version> --parcel <version> [--dist <distro>]"
  echo "        $1 [-h|--help]"
  echo ""
  echo "   ex.  $1 --airflow 1.10.3 --python 3.6.9 --parcel b0 --dist centos7"
  exit 1
}

# process commandline arguments
while [[ $1 = -* ]]; do
  case $1 in
    -a|--airflow)
      shift
      AIRFLOW_VERSION=$1
      ;;
    -p|--python)
      shift
      PYTHON_VERSION=$1
      ;;
    -P|--parcel)
      shift
      PARCEL_VERSION=$1
      ;;
    -d|--dist)
      shift
      DISTROS_TO_BUILD=$1
      ;;
    -h|--help)
      print_usage "$(basename "$0")"
      ;;
    *)
      print_usage "$(basename "$0")"
      ;;
  esac
  shift
done

# validate provided parameters
if [[ -z "$AIRFLOW_VERSION" ]] || [[ -z "$PYTHON_VERSION" ]] || [[ -z "$PARCEL_VERSION" ]]; then
  print_usage "$(basename "$0")"
fi

# default to building for all distros if none is provided
if [[ -z "$DISTROS_TO_BUILD" ]]; then
  DISTROS_TO_BUILD=(centos6 centos7 debian8 ubuntu1404 ubuntu1604 ubuntu1804)
fi

# get the directory of this bash file
BASEDIR="$( cd "$( dirname "$0" )" && pwd )"

# ensure output folders exist
mkdir -p "${BASEDIR}/tmp"
mkdir -p "${BASEDIR}/target"

# download python source code
echo "*** Downloading Python-${PYTHON_VERSION} source ..."
if command -v wget; then
  wget -c "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz" -P ${BASEDIR}/tmp
  wget -c "https://bootstrap.pypa.io/get-pip.py" -P ${BASEDIR}/tmp
else
  echo "ERROR: please install wget"
  exit 10
fi

# don't continue to next distribution if a docker run fails
set -euo pipefail

# build parcels for each linux distribution
for DISTRO in ${DISTROS_TO_BUILD}; do
  # build/tag the corresponding Dockerfile
  echo "*** Building Dockerfile for ${DISTRO} ..."
  docker build \
    -f "${BASEDIR}/docker/${DISTRO}/Dockerfile" \
    -t teamclairvoyant/airflow-cloudera-parcel-build-${DISTRO} \
    .

  # create airflow parcel
  echo "*** Building Airflow-${AIRFLOW_VERSION} parcel for ${DISTRO} ..."
  docker run \
    -it \
    --rm  \
    --volume "${BASEDIR}":/build \
    teamclairvoyant/airflow-cloudera-parcel-build-${DISTRO} \
    /build/docker_entrypoint.sh \
      --airflow ${AIRFLOW_VERSION} \
      --python ${PYTHON_VERSION} \
      --parcel ${PARCEL_VERSION} \
      --dist ${DISTRO}
done

echo "*** Creating manifest.json in target/ directory ..."
${BASEDIR}/make_manifest.py ${BASEDIR}/target/
