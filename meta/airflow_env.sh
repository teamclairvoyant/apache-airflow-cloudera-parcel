#!/bin/bash
AIRFLOW_DIRNAME=${PARCEL_DIRNAME:-"AIRFLOW-{{ version }}"}

export AIRFLOW_DIR="${PARCELS_ROOT}/${PARCEL_DIRNAME}"
export PATH="${AIRFLOW_DIR}/bin:${PATH}"
export PYTHONHOME="${AIRFLOW_DIR}"
export PYTHONPATH="${AIRFLOW_DIR}/lib/pythonPYVER"

if [ -z "${AIRFLOW_PYTHON}" ]; then
  export AIRFLOW_PYTHON="${AIRFLOW_DIR}/bin/pythonPYVER"
fi

