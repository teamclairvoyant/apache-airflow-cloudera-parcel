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
shopt -s extglob # enable extended pattern matching

print_usage() {
  echo "Usage:  $1 --airflow <version> --python <version> --parcel <version> --dist <distribution>"
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
      DIST=$1
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

# validate linux distribution, and map to cloudera parcel name
case ${DIST} in
  centos6|rhel6)
    PARCEL_DIST=el6
    ;;
  centos7|rhel7)
    PARCEL_DIST=el7
    ;;
  debian8)
    PARCEL_DIST=jessie
    ;;
  ubuntu1404)
    PARCEL_DIST=trusty
    ;;
  ubuntu1604)
    PARCEL_DIST=xenial
    ;;
  ubuntu1804)
    PARCEL_DIST=bionic
    ;;
  *)
   echo "ERROR: '$1' is not a supported linux distribution."
   exit 1
   ;;
esac

# validate python version, and extract major and minor version
case ${PYTHON_VERSION} in
  3.+([0-9]).+([0-9]))
    PYTHON_VERSION_SHORT=$(echo ${PYTHON_VERSION} | awk -F. '{print $1"."$2}')
    ;;
  2.+([0-9]).+([0-9]))
    echo "ERROR: airflow only supports Python 3"
    exit 1
    ;;
  *)
    echo "ERROR: ${PYTHON_VERSION} is not a valid python version"
    exit 1
    ;;
esac

# prepare the parcel install directory
PARCEL_DIR=/opt/cloudera/parcels
PARCEL_VERSION=${AIRFLOW_VERSION}-python${PYTHON_VERSION}_${PARCEL_VERSION}
PARCEL_NAME=AIRFLOW-${PARCEL_VERSION}
INSTALL_DIR=${PARCEL_DIR}/${PARCEL_NAME}
WORKING_DIR=${INSTALL_DIR}.working
mkdir -p ${INSTALL_DIR}
mkdir -p ${WORKING_DIR}

# compile/install python
tar -xvf /build/tmp/Python-${PYTHON_VERSION}.tar.xz -C ${WORKING_DIR}
cd ${WORKING_DIR}/Python-${PYTHON_VERSION}
./configure --prefix=${INSTALL_DIR} --without-ensurepip
make && make install

# add parcel bin to path
PATH=${INSTALL_DIR}/bin:${PATH}

# install pip
python${PYTHON_VERSION_SHORT} /build/tmp/get-pip.py

# install flask
# we do this because Airflow 1.10.3 pins an old version of werkzeug, causing issues with Flask
# SEE: https://github.com/apache/airflow/pull/5535
pip install Flask==1.0.3

# install airflow
# we use "devel_ci" because it includes all plugins, except those not compatible with Python 3 (like snakebite)
pip install apache-airflow[devel_ci]==${AIRFLOW_VERSION}

# copy parcel metadata
cp -r /build/meta/ ${INSTALL_DIR}/meta/

# update parcel metadata
sed -i -e "s/__PARCEL_VERSION__/${PARCEL_VERSION}/g" ${INSTALL_DIR}/meta/parcel.json
sed -i -e "s/__PARCEL_NAME__/${PARCEL_NAME}/g" -e "s/__PYTHON_VERSION_SHORT__/${PYTHON_VERSION_SHORT}/g" ${INSTALL_DIR}/meta/airflow_env.sh

# package parcel and calculate hash
cd ${PARCEL_DIR}
tar -czf /build/target/${PARCEL_NAME}-${PARCEL_DIST}.parcel ${PARCEL_NAME}
sha1sum /build/target/${PARCEL_NAME}-${PARCEL_DIST}.parcel | awk '{print $1}' >/build/target/${PARCEL_NAME}-${PARCEL_DIST}.parcel.sha