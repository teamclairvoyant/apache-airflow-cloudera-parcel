#!/bin/bash
set -euo pipefail

# These are picked up from the Docker ENV.
AIRFLOW_DIR=${INSTALL_DIR}/${PARCEL_NAME}
PATH="${AIRFLOW_DIR}/bin:${PATH}"
PIPOPTS=""
#export SLUGIFY_USES_TEXT_UNIDECODE=no
export AIRFLOW_GPL_UNIDECODE=yes

PYVER=$(echo $PYTHON_VERSION | awk -F. '{print $1"."$2}')
PYMAJVER=$(echo $PYTHON_VERSION | awk -F. '{print $1}')

echo "*** Installing Airflow..."
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow==${AIRFLOW_VERSION}

echo "*** Installing Airflow plugins..."
echo "** Installing Airflow[celery]."
#${AIRFLOW_DIR}/bin/pip $PIPOPTS install 'celery<4'
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow[celery]
echo "** Installing Airflow[mysql]."
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow[mysql]
echo "** Installing Airflow[postgres]."
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow[postgres]
echo "** Installing Airflow[kerberos]."
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow[kerberos]
echo "** Installing Airflow[crypto]."
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow[crypto]
echo "** Installing Airflow[hive]."
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow[hive]
echo "** Installing Airflow[password]."
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow[password]
echo "** Installing Airflow[rabbitmq]."
${AIRFLOW_DIR}/bin/pip $PIPOPTS install apache-airflow[rabbitmq]

