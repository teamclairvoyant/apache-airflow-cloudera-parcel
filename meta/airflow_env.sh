#!/usr/bin/env bash
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
AIRFLOW_DIRNAME=${PARCEL_DIRNAME:-"__PARCEL_NAME__"}
PYTHON_VERSION_SHORT="__PYTHON_VERSION_SHORT__"

export AIRFLOW_DIR="${PARCELS_ROOT}/${PARCEL_DIRNAME}"
export PATH="${AIRFLOW_DIR}/bin:${PATH}"
export PYTHONHOME="${AIRFLOW_DIR}"
export PYTHONPATH="${AIRFLOW_DIR}/lib/python${PYTHON_VERSION_SHORT}"