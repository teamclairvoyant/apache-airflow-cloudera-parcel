FROM centos:centos6
LABEL maintainer="michael.arnold@clairvoyantsoft.com"

ENV DIST centos6
ENV PARCEL_DIST el6
ENV INSTALL_DIR /opt/cloudera/parcels

WORKDIR /BUILD

RUN yum -y -e1 -d1 install https://download.postgresql.org/pub/repos/yum/reporpms/EL-6-x86_64/pgdg-redhat-repo-latest.noarch.rpm

#RUN yum -y -e1 -d1 update
RUN yum -y -e1 -d1 groupinstall "Development Tools"
RUN yum -y -e1 -d1 install readline-devel \
                           tk-devel \
                           gdbm-devel \
                           db4-devel \
                           libpcap-devel \
                           libffi-devel \
                           xz-devel \
                           expat-devel \
                           zlib-devel \
                           bzip2-devel \
                           openssl-devel \
                           ncurses-devel \
                           sqlite-devel \
                           cyrus-sasl-devel.x86_64 \
                           mysql-devel \
                           libpqxx-devel \
                           gcc \
                           postgresql94

ENV PATH=$PATH:/usr/pgsql-9.4/bin                   

ARG AIRFLOW_VERSION
ENV AIRFLOW_VERSION ${AIRFLOW_VERSION:-1.10.0}
ARG PYTHON_VERSION
ENV PYTHON_VERSION ${PYTHON_VERSION:-2.7.15}
ARG PARCEL_VERSION
ENV PARCEL_VERSION ${PARCEL_VERSION:-b0}
ENV PARCEL_NAME AIRFLOW-${AIRFLOW_VERSION}-python${PYTHON_VERSION}_${PARCEL_VERSION}

COPY Python-${PYTHON_VERSION}.tar.xz /BUILD/
RUN tar xJf /BUILD/Python-${PYTHON_VERSION}.tar.xz -C /BUILD

COPY docker/${DIST}/compile_python.sh /BUILD
RUN mkdir -p ${INSTALL_DIR}/${PARCEL_NAME} && \
    cd /BUILD/Python-${PYTHON_VERSION} && \
    . /BUILD/compile_python.sh && \
    ./configure --prefix=${INSTALL_DIR}/${PARCEL_NAME} && \
    make && \
    make install
#    DESTDIR=/BUILD/${PARCEL_NAME} make install

COPY get-pip.py /BUILD/get-pip.py
RUN PYVER=$(echo $PYTHON_VERSION | awk -F. '{print $1"."$2}') && \
    ${INSTALL_DIR}/${PARCEL_NAME}/bin/python${PYVER} /BUILD/get-pip.py

COPY docker/install_airflow.sh /BUILD
RUN bash -x /BUILD/install_airflow.sh

COPY meta/ ${INSTALL_DIR}/${PARCEL_NAME}/meta/
RUN PYVER=$(echo $PYTHON_VERSION | awk -F. '{print $1"."$2}') && \
    sed -e "/\"version\":/s|VERSION|${AIRFLOW_VERSION}-python${PYTHON_VERSION}_${PARCEL_VERSION}|" \
        -i ${INSTALL_DIR}/${PARCEL_NAME}/meta/parcel.json && \
    sed -e "/AIRFLOW_DIRNAME/s|VERSION|${AIRFLOW_VERSION}-python${PYTHON_VERSION}_${PARCEL_VERSION}|" \
        -e "s|PYVER|${PYVER}|" \
        -i ${INSTALL_DIR}/${PARCEL_NAME}/meta/airflow_env.sh

COPY docker/modify_buildroot.sh /BUILD
RUN bash -x /BUILD/modify_buildroot.sh

RUN cd ${INSTALL_DIR} && \
    tar zcf /BUILD/${PARCEL_NAME}-${PARCEL_DIST}.parcel ${PARCEL_NAME} && \
    sha1sum /BUILD/${PARCEL_NAME}-${PARCEL_DIST}.parcel | awk '{print $1}' >/BUILD/${PARCEL_NAME}-${PARCEL_DIST}.parcel.sha

CMD /bin/bash

