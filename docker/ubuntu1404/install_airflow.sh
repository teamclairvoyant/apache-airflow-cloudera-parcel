#!/bin/bash
set -euo pipefail

airflow_parcel_name=AIRFLOW-${PARCEL_VERSION}_${AIRFLOW_VERSION}_${PYTHON_VERSION}
full_path=/BUILD/${airflow_parcel_name}
PIPOPTS=""
#export SLUGIFY_USES_TEXT_UNIDECODE=no
export AIRFLOW_GPL_UNIDECODE=yes

echo "*** Installing Airflow..."
${full_path}/bin/pip $PIPOPTS install apache-airflow==${AIRFLOW_VERSION}

echo "*** Installing Airflow plugins..."
echo "** Installing Airflow[celery]."
#${full_path}/bin/pip $PIPOPTS install 'celery<4'
${full_path}/bin/pip $PIPOPTS install apache-airflow[celery]
echo "** Installing Airflow[mysql]."
${full_path}/bin/pip $PIPOPTS install apache-airflow[mysql]
echo "** Installing Airflow[postgres]."
${full_path}/bin/pip $PIPOPTS install apache-airflow[postgres]
echo "** Installing Airflow[kerberos]."
${full_path}/bin/pip $PIPOPTS install apache-airflow[kerberos]
echo "** Installing Airflow[crypto]."
${full_path}/bin/pip $PIPOPTS install apache-airflow[crypto]
echo "** Installing Airflow[hive]."
${full_path}/bin/pip $PIPOPTS install apache-airflow[hive]
echo "** Installing Airflow[password]."
${full_path}/bin/pip $PIPOPTS install apache-airflow[password]
echo "** Installing Airflow[rabbitmq]."
${full_path}/bin/pip $PIPOPTS install apache-airflow[rabbitmq]

