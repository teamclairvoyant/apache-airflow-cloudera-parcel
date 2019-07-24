#!/bin/bash
set -euo pipefail

# These are picked up from the Docker ENV.
AIRFLOW_DIR=${INSTALL_DIR}/${PARCEL_NAME}
#PYVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1"."$2}')
#PYMAJVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1}')

PATH="${AIRFLOW_DIR}/bin:${PATH}"
PIPOPTS=""

echo "*** Installing iniparse..."
pip $PIPOPTS install iniparse

echo "*** Installing crudini..."
install -m 0755 -o root -g root crudini "${AIRFLOW_DIR}/bin/crudini"

echo "*** Updating the shebang..."
sed -e "1s|.*|#!${AIRFLOW_DIR}/python${PYVER}|" -i "${AIRFLOW_DIR}/bin/crudini"

