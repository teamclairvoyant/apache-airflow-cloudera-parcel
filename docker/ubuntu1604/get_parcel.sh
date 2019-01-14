#!/bin/bash
VERSION=0.0.0_1.10.1_2.7.15
DIST=ubuntu1604
PARCEL_DIST=xenial
NAME=airflow-${DIST}
IMAGE=airflow/${DIST}

if [ ! -d target ]; then mkdir target; fi
docker run -d --name ${NAME} ${IMAGE}
docker cp ${NAME}:/BUILD/AIRFLOW-${VERSION}-${PARCEL_DIST}.parcel target/
docker cp ${NAME}:/BUILD/AIRFLOW-${VERSION}-${PARCEL_DIST}.parcel.sha target/
docker rm ${NAME}

