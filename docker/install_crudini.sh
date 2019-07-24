#!/bin/bash
set -euo pipefail

# These are picked up from the Docker ENV.
AIRFLOW_DIR=${INSTALL_DIR}/${PARCEL_NAME}
PYVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1"."$2}')
#PYMAJVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1}')

PATH="${AIRFLOW_DIR}/bin:${PATH}"
PIPOPTS=""

echo "*** Installing iniparse..."
pip $PIPOPTS install iniparse

echo "*** Installing crudini..."
install -m 0755 -o root -g root crudini "${AIRFLOW_DIR}/bin/.crudini"

echo "*** Updating the shebang..."
sed -e "1s|.*|#!${AIRFLOW_DIR}/bin/python|" -i "${AIRFLOW_DIR}/bin/.crudini"

echo "*** Installing crudini shell wrapper..."
install -m 0755 -o root -g root /dev/null "${AIRFLOW_DIR}/bin/crudini"
cat <<EOF >"${AIRFLOW_DIR}/bin/crudini"
#!/bin/bash
export PATH=${AIRFLOW_DIR}/bin:\$PATH
export PYTHONHOME=${AIRFLOW_DIR}
export PYTHONPATH=${AIRFLOW_DIR}/lib/python${PYVER}

exec ${AIRFLOW_DIR}/bin/.crudini \$@
EOF

