#!/bin/bash
set -euo pipefail
# These are picked up from the Docker ENV.
AIRFLOW_DIR=${INSTALL_DIR}/${PARCEL_NAME}

PYVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1"."$2}')

echo "Updating the shebang..."
for FILE in $(file "${AIRFLOW_DIR}"/bin/* | awk -F: '/Python script, .* text executable/ || /a .*\/AIRFLOW-.* script.* text executable/ {print $1}'); do
  sed -e "1s|.*|#!/usr/bin/env python${PYVER}|" -i "$FILE"
done

echo "Creating ${AIRFLOW_DIR}/etc/airflow/conf.dist ..."
install -m 0755 -o root -g root -d "${AIRFLOW_DIR}/etc/airflow/conf.dist"

echo "*** Installing mkuser.py..."
install -m 0755 -o root -g root mkuser.py "${AIRFLOW_DIR}/bin/mkuser.py"

echo "Creating ${AIRFLOW_DIR}/bin/airflow-mkuser.sh ..."
install -m 0755 -o root -g root /dev/null "${AIRFLOW_DIR}/bin/airflow-mkuser.sh"
cat <<EOF >"${AIRFLOW_DIR}/bin/airflow-mkuser.sh"
#!/bin/bash
export PATH=${AIRFLOW_DIR}/bin:\$PATH
export PYTHONHOME=${AIRFLOW_DIR}
export PYTHONPATH=${AIRFLOW_DIR}/lib/python${PYVER}

# AIRFLOW_HOME
if [ -f /etc/airflow/conf/airflow-env.sh ]; then
  . /etc/airflow/conf/airflow-env.sh
else
  export AIRFLOW_HOME=/var/lib/airflow
  export AIRFLOW_CONFIG=/etc/airflow/conf/airflow.cfg
fi

exec ${AIRFLOW_DIR}/bin/mkuser.py \$@
EOF

echo "Creating ${AIRFLOW_DIR}/bin/airflow-cm.sh ..."
install -m 0755 -o root -g root /dev/null "${AIRFLOW_DIR}/bin/airflow-cm.sh"
cat <<EOF >"${AIRFLOW_DIR}/bin/airflow-cm.sh"
#!/bin/bash
#
# This should only be run by Cloudera Manager.
#
if [ -z "\${CONF_DIR}" ]; then
  echo "ERROR: This script must be run from Cloudera Manager."
  exit 1
fi

export PATH=${AIRFLOW_DIR}/bin:\$PATH
export PYTHONHOME=${AIRFLOW_DIR}
export PYTHONPATH=${AIRFLOW_DIR}/lib/python${PYVER}

if [ -f \${CONF_DIR}/airflow-env.sh ]; then
  . \${CONF_DIR}/airflow-env.sh
fi

echo "* AIRFLOW_DIR: $AIRFLOW_DIR"
echo "* AIRFLOW_HOME: \$AIRFLOW_HOME"
echo "* AIRFLOW_CONFIG: \$AIRFLOW_CONFIG"
echo "* CONF_DIR: \$CONF_DIR"

exec ${AIRFLOW_DIR}/bin/.airflow \$@
EOF

echo "Creating ${AIRFLOW_DIR}/etc/airflow/conf.dist/airflow.cfg ..."
export AIRFLOW_HOME=/var/lib/airflow
install -m 0755 -o root -g root -d "${AIRFLOW_HOME}"
install -m 0755 -o root -g root -d /etc/airflow/conf/
"${AIRFLOW_DIR}/bin/airflow" initdb
install -m 0755 -o root -g root -d "${AIRFLOW_DIR}/etc/airflow/conf.dist/"
install -m 0644 -o root -g root "/etc/airflow/conf/airflow.cfg" "${AIRFLOW_DIR}/etc/airflow/conf.dist/"

rm -f "${AIRFLOW_DIR}/LICENSE"

