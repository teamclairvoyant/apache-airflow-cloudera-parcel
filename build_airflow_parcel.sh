#!/bin/bash
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
if [ -n "$DEBUG" ]; then set -x; fi
#
##### START CONFIG ###################################################

##### STOP CONFIG ####################################################
PATH=/usr/bin:/usr/sbin:/bin:/sbin:/usr/local/bin

# Function to print the help screen.
print_help() {
  echo "Usage:  $1 --airflow <version> --python <version> --parcel <version>"
  echo "        $1 [-h|--help]"
  echo "        $1 [-v|--version]"
  echo ""
  echo "   ex.  $1 --airflow 1.10.1 --python 3.5.6 --parcel b0"
  exit 1
}

# Function to check for root priviledges.
check_root() {
  if [[ $(/usr/bin/id | awk -F= '{print $2}' | awk -F"(" '{print $1}' 2>/dev/null) -ne 0 ]]; then
    echo "You must have root priviledges to run this program."
    exit 2
  fi
}

## If the variable DEBUG is set, then turn on tracing.
## http://www.research.att.com/lists/ast-users/2003/05/msg00009.html
#if [ $DEBUG ]; then
#  # This will turn on the ksh xtrace option for mainline code
#  set -x
#
#  # This will turn on the ksh xtrace option for all functions
#  typeset +f |
#  while read F junk
#  do
#    typeset -ft $F
#  done
#  unset F junk
#fi

# Process arguments.
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
    -h|--help)
      print_help "$(basename "$0")"
      ;;
    -v|--version)
      echo "Builds a parcel of Airflow for Cloudera Manager."
      exit 0
      ;;
    *)
      print_help "$(basename "$0")"
      ;;
  esac
  shift
done

# Check to see if we have the required parameters.
if [ -z "$AIRFLOW_VERSION" ] || [ -z "$PYTHON_VERSION" ] || [ -z "$PARCEL_VERSION" ]; then print_help "$(basename "$0")"; fi

# Lets not bother continuing unless we have the privs to do something.
#check_root

# main
set -euo pipefail
echo "*** Linting JSON files ..."
for FILE in meta/*json; do
  echo "** $FILE"
  jsonlint -q "$FILE"
done

echo "*** Validating parcel files ..."
java -jar ../../cloudera/cm_ext/validator/target/validator.jar -a meta/alternatives.json
java -jar ../../cloudera/cm_ext/validator/target/validator.jar -p meta/parcel.json
java -jar ../../cloudera/cm_ext/validator/target/validator.jar -r meta/permissions.json

if command -v wget; then
  GET="wget -c"
elif command -v curl; then
  GET="curl -LOR"
else
  echo "ERROR: Missing wget or curl."
  exit 10
fi
if [ ! -f "Python-${PYTHON_VERSION}.tar.xz" ]; then
  echo "*** Downloading Python ${PYTHON_VERSION} sourcecode ..."
  ${GET} "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz"
fi
if [ ! -f get-pip.py ]; then
  echo "*** Downloading get-pip.py ..."
  ${GET} https://bootstrap.pypa.io/get-pip.py
fi
if [ ! -f crudini ]; then
  echo "*** Downloading crudini ..."
  ${GET} https://raw.githubusercontent.com/pixelb/crudini/master/crudini
fi
if [ ! -d target ]; then mkdir target; fi

for DIST in centos6 centos7 debian8 ubuntu1404 ubuntu1604 ubuntu1804; do
  case $DIST in
    centos6)    PARCEL_DIST=el6    ;;
    centos7)    PARCEL_DIST=el7    ;;
    debian7)    PARCEL_DIST=wheezy ;;
    debian8)    PARCEL_DIST=jessie ;;
    ubuntu1404) PARCEL_DIST=trusty ;;
    ubuntu1604) PARCEL_DIST=xenial ;;
    ubuntu1804) PARCEL_DIST=bionic ;;
  esac
  PARCEL_NAME=AIRFLOW-${AIRFLOW_VERSION}-python${PYTHON_VERSION}_${PARCEL_VERSION}

  echo "*** Building Airflow ${AIRFLOW_VERSION} parcel for ${DIST} ..."
  docker build -f docker/${DIST}/Dockerfile -t "airflow/${DIST}:${AIRFLOW_VERSION}-python${PYTHON_VERSION}_${PARCEL_VERSION}" \
    --build-arg AIRFLOW_VERSION="$AIRFLOW_VERSION" \
    --build-arg PYTHON_VERSION="$PYTHON_VERSION" \
    --build-arg PARCEL_VERSION="$PARCEL_VERSION" .

  echo "*** Extracting Airflow parcel ${PARCEL_VERSION} for ${DIST} ..."
  docker run -d --name airflow-${DIST} "airflow/${DIST}:${AIRFLOW_VERSION}-python${PYTHON_VERSION}_${PARCEL_VERSION}"
  docker cp "airflow-${DIST}:/BUILD/${PARCEL_NAME}-${PARCEL_DIST}.parcel" target/
  docker cp "airflow-${DIST}:/BUILD/${PARCEL_NAME}-${PARCEL_DIST}.parcel.sha" target/
  docker rm airflow-${DIST}
done

echo "*** Creating manifest.json in target/ directory ..."
./make_manifest.py target/

