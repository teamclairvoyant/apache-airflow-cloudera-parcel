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
FROM debian:8

LABEL maintainer="michael.arnold@clairvoyantsoft.com"

# install build dependancies
ARG DEBIAN_FRONTEND=noninteractive
RUN set -ex \
    && apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y libbz2-dev \
                          libexpat1-dev \
                          libffi-dev \
                          libgdbm-dev \
                          libkrb5-dev \
                          liblzma-dev \
                          libmysqlclient-dev \
                          libncursesw5-dev \
                          libpcap-dev \
                          libpq-dev \
                          libreadline-dev \
                          libsasl2-dev \
                          libsqlite3-dev \
                          libssl-dev \
                          tk-dev \
                          wget \
                          xz-utils \
    && apt-get clean

WORKDIR /build
