FROM centos:centos6
LABEL maintainer="michael.arnold@clairvoyantsoft.com"

ENV DIST centos6
ENV PARCEL_DIST el6
ENV PARCEL_VERSION 0.0.0
ENV AIRFLOW_VERSION 1.10.1
ENV PYTHON_VERSION 2.7.15
ENV PARCEL_PATCH_VERSION p0
ENV PARCEL_NAME AIRFLOW-${PARCEL_VERSION}_${AIRFLOW_VERSION}_${PYTHON_VERSION}

WORKDIR /BUILD

RUN yum -y -e1 -d1 update
RUN yum -y -e1 -d1 groupinstall "development tools"
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
                           postgresql-devel

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

