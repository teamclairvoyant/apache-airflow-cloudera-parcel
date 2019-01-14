#!/bin/bash
./get_python.sh
docker build -f docker/centos6/Dockerfile -t airflow/centos6 .
docker/centos6/get_parcel.sh
docker build -f docker/centos7/Dockerfile -t airflow/centos7 .
docker/centos7/get_parcel.sh
docker build -f docker/debian7/Dockerfile -t airflow/debian7 .
docker/debian7/get_parcel.sh
docker build -f docker/debian8/Dockerfile -t airflow/debian8 .
docker/debian8/get_parcel.sh
docker build -f docker/ubuntu1404/Dockerfile -t airflow/ubuntu1404 .
docker/ubuntu1404/get_parcel.sh
docker build -f docker/ubuntu1604/Dockerfile -t airflow/ubuntu1604 .
docker/ubuntu1604/get_parcel.sh
./make_manifest.py target/
