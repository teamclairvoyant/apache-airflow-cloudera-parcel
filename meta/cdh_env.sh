export AIRFLOW_DIR="$PARCELS_ROOT/$PARCEL_DIRNAME"
export PYTHONPATH=${AIRFLOW_DIR}/lib/python2.7/site-packages:$PATH

echo "Updating the shebang..."
sed -i '1s+.*+#!'"${AIRFLOW_DIR}"'/bin/python2.7+' ${AIRFLOW_DIR}/bin/airflow
echo "Exit code for airflow shebang updation is $?"
sed -i '1s+.*+#!'"${AIRFLOW_DIR}"'/bin/python2.7+' ${AIRFLOW_DIR}/bin/gunicorn
echo "Exit code for gunicorn shebang updation is $?"

echo "export PYTHONPATH=${PYTHONPATH}" >> ${AIRFLOW_DIR}/bin/airflow.sh
echo "export PATH=${AIRFLOW_DIR}/bin:\$PATH" >> ${AIRFLOW_DIR}/bin/airflow.sh
echo "${AIRFLOW_DIR}/bin/airflow \$@" >> ${AIRFLOW_DIR}/bin/airflow.sh