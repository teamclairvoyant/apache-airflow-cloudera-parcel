FROM ubuntu:16.04
LABEL maintainer="michael.arnold@clairvoyantsoft.com"

ENV DIST ubuntu1604
ENV PARCEL_DIST xenial
ENV PARCEL_VERSION 0.0.0
ENV AIRFLOW_VERSION 1.10.1
ENV PYTHON_VERSION 2.7.15
ENV PARCEL_PATCH_VERSION p0
ENV PARCEL_NAME AIRFLOW-${PARCEL_VERSION}_${AIRFLOW_VERSION}_${PYTHON_VERSION}
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /BUILD

RUN apt-get update && apt-get install -y build-essential
RUN apt-get update && apt-get install -y libreadline-dev \
                           tk-dev \
                           libgdbm-dev \
                           libdb-dev \
                           libpcap-dev \
                           libffi-dev \
                           liblzma-dev \
                           libexpat1-dev \
                           libzlcore-dev \
                           libbz2-dev \
                           libssl-dev \
                           libncurses5-dev \
                           libsqlite3-dev \
                           libsasl2-dev \
                           libmysqlclient-dev \
                           libpq-dev \
                           libkrb5-dev \
                           curl \
                           file

COPY Python-${PYTHON_VERSION}.tar.xz /BUILD/
RUN tar xJf /BUILD/Python-${PYTHON_VERSION}.tar.xz -C /BUILD
#RUN curl -L -o /BUILD/Python-${PYTHON_VERSION}.tar.xz https://python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz && \
#    tar xJf /BUILD/Python-${PYTHON_VERSION}.tar.xz -C /BUILD && \
#    rm -f /BUILD/Python-${PYTHON_VERSION}.tar.xz

COPY README.md /BUILD/${PARCEL_NAME}/
COPY docker/${DIST}/compile_python.sh /BUILD
#RUN cd /BUILD/Python-${PYTHON_VERSION} && . /BUILD/compile_python.sh && ./configure --prefix=/opt/cloudera/parcels/${PARCEL_NAME} && make && DESTDIR=/BUILD/${PARCEL_NAME} make altinstall
RUN cd /BUILD/Python-${PYTHON_VERSION} && . /BUILD/compile_python.sh && ./configure --prefix=/BUILD/${PARCEL_NAME} && make && make altinstall

ADD https://bootstrap.pypa.io/get-pip.py /BUILD/get-pip.py
RUN /BUILD/${PARCEL_NAME}/bin/python2.7 /BUILD/get-pip.py

COPY docker/${DIST}/install_airflow.sh /BUILD
RUN bash -x /BUILD/install_airflow.sh

COPY meta/ /BUILD/${PARCEL_NAME}/meta/
#RUN sed -e "/\"version\":/s|VERSION|${PARCEL_VERSION}-airflow${AIRFLOW_VERSION}-python${PYTHON_VERSION}|" \
RUN sed -e "/\"version\":/s|VERSION|${PARCEL_VERSION}_${AIRFLOW_VERSION}_${PYTHON_VERSION}|" \
        -i /BUILD/${PARCEL_NAME}/meta/parcel.json

RUN tar zcf ${PARCEL_NAME}-${PARCEL_DIST}.parcel ${PARCEL_NAME} && sha1sum ${PARCEL_NAME}-${PARCEL_DIST}.parcel | awk '{print $1}' >${PARCEL_NAME}-${PARCEL_DIST}.parcel.sha

CMD /bin/bash

