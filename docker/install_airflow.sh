#!/bin/bash
set -euo pipefail

# These are picked up from the Docker ENV.
AIRFLOW_DIR=${INSTALL_DIR}/${PARCEL_NAME}
PYVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1"."$2}')
PYMAJVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1}')

PATH="${AIRFLOW_DIR}/bin:${PATH}"
PIPOPTS=""
#export SLUGIFY_USES_TEXT_UNIDECODE=no
export AIRFLOW_GPL_UNIDECODE=yes

echo "** Installing numpy."
pip $PIPOPTS install numpy
echo "** Installing setuptools."
pip $PIPOPTS install -U setuptools
echo "** Installing psycopg2-binary"
pip $PIPOPTS install psycopg2-binary

echo "*** Installing Airflow..."
if [ "$PYMAJVER" -lt 3 ]; then
  # Pandas >0.22.0 breaks Python 2.x support.
  pip $PIPOPTS install pandas=="0.22.0"
fi
# Flask >1.0.3 breaks Airflow
pip $PIPOPTS install Flask==1.0.3
pip $PIPOPTS install apache-airflow=="${AIRFLOW_VERSION}"

echo "*** Installing Airflow plugins..."
echo "** Installing Airflow[celery]."
pip $PIPOPTS install 'apache-airflow[celery]'
echo "** Installing Airflow[mysql]."
pip $PIPOPTS install 'apache-airflow[mysql]'
echo "** Installing Airflow[postgres]."
pip $PIPOPTS install 'apache-airflow[postgres]'
echo "** Installing Airflow[kerberos]."
pip $PIPOPTS install 'apache-airflow[kerberos]'
echo "** Installing Airflow[crypto]."
pip $PIPOPTS install 'apache-airflow[crypto]'
echo "** Installing Airflow[hive]."
pip $PIPOPTS install 'apache-airflow[hive]'
echo "** Installing Airflow[password]."
pip $PIPOPTS install 'apache-airflow[password]'
echo "** Installing Airflow[rabbitmq]."
pip $PIPOPTS install 'apache-airflow[rabbitmq]'

echo "*** Installing airflow..."
mv "${AIRFLOW_DIR}/bin/airflow" "${AIRFLOW_DIR}/bin/.airflow"

echo "*** Installing airflow shell wrapper..."
install -m 0755 -o root -g root /dev/null "${AIRFLOW_DIR}/bin/airflow"
cat <<EOF >"${AIRFLOW_DIR}/bin/airflow"
#!/bin/bash
export PATH=${AIRFLOW_DIR}/bin:\$PATH
export PYTHONHOME=${AIRFLOW_DIR}
export PYTHONPATH=${AIRFLOW_DIR}/lib/python${PYVER}

# AIRFLOW_HOME & AIRFLOW_CONFIG
if [ -f /etc/airflow/conf/airflow-env.sh ]; then
  . /etc/airflow/conf/airflow-env.sh
else
  export AIRFLOW_HOME=/var/lib/airflow
  export AIRFLOW_CONFIG=/etc/airflow/conf/airflow.cfg
fi

exec ${AIRFLOW_DIR}/bin/.airflow \$@
EOF

