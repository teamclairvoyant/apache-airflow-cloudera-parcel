#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright Clairvoyant 2019
#
FROM centos:7

LABEL maintainer="michael.arnold@clairvoyantsoft.com"

# install build dependancies
RUN set -ex \
    && yum -y update \
    && yum -y groupinstall development \
    && yum -y install bzip2-devel \
                      cyrus-sasl-devel \
                      expat-devel \
                      gdbm-devel \
                      krb5-devel \
                      libffi-devel \
                      libpcap-devel \
                      mysql-devel \
                      openssl-devel \
                      postgresql-devel \
                      readline-dev \
                      sqlite-devel \
                      tk-devel \
                      wget \
                      xz-devel \
                      zlib-devel \
    && yum clean all

WORKDIR /build
