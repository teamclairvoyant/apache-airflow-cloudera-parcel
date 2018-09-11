export AIRFLOW_DIR="$PARCELS_ROOT/$PARCEL_DIRNAME"
export PATH=${AIRFLOW_DIR}/usr/local/bin:$PATH

sed -i '1s+.*+#!'"${AIRFLOW_DIR}"'/usr/local/bin/python2.7+' ${AIRFLOW_DIR}/usr/local/bin/airflow
sed -i '1s+.*+#!'"${AIRFLOW_DIR}"'/usr/local/bin/python2.7+' ${AIRFLOW_DIR}/usr/local/bin/gunicorn
