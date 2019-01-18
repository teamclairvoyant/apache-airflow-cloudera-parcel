#!/bin/bash
set -euo pipefail

# These are picked up from the Docker ENV.
AIRFLOW_DIR=${INSTALL_DIR}/${PARCEL_NAME}
#PYVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1"."$2}')
#PYMAJVER=$(echo "$PYTHON_VERSION" | awk -F. '{print $1}')

PATH="${AIRFLOW_DIR}/bin:${PATH}"
PIPOPTS=""
#export SLUGIFY_USES_TEXT_UNIDECODE=no
export AIRFLOW_GPL_UNIDECODE=yes

echo "*** Installing Airflow..."
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

