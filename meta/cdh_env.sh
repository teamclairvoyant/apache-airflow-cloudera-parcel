export AIRFLOW_DIR="$PARCELS_ROOT/$PARCEL_DIRNAME"
export PYTHONPATH=${AIRFLOW_DIR}/usr/lib/python2.7/site-packages:$PATH

echo "Updating the shebang..."
sed -i '1s+.*+#!'"${AIRFLOW_DIR}"'/usr/bin/python2.7+' ${AIRFLOW_DIR}/usr/bin/airflow
echo "Exit code for airflow shebang updation is $?"
sed -i '1s+.*+#!'"${AIRFLOW_DIR}"'/usr/bin/python2.7+' ${AIRFLOW_DIR}/usr/bin/gunicorn
echo "Exit code for gunicorn shebang updation is $?"