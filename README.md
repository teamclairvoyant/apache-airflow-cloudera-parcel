# Airflow [Parcel](https://github.com/cloudera/cm_ext/wiki/Parcels:-What-and-Why%3F)

This repository allows you to install [Apache Airflow](https://airflow.apache.org/) as a parcel deployable by [Cloudera Manager](https://www.cloudera.com/products/product-components/cloudera-manager.html).

## Requirements
- A supported operating system.
- MySQL or PostgreSQL database in which to store Airflow metadata.

### Currently Supported Versions of Airflow
- Airflow 1.9.0
- Airflow 1.10.3

### Currently Supported Operating Systems
- CentOS/RHEL 6 & 7
- Debian 8
- Ubuntu 14.04, 16.04, & 18.04

## Installing the Parcel
0. First, install the [Airflow CSD](https://github.com/teamclairvoyant/apache-airflow-cloudera-csd).  Then you can skip steps #1 and #2.
1. In Cloudera Manager, go to `Hosts -> Parcels -> Configuration`.
2. Add `http://archive.clairvoyantsoft.com/airflow/parcels/latest/` to the Remote Parcel Repository URLs if it does not yet exist.
3. In Cloudera Manager, go to `Hosts -> Parcels`.  Airflow parcels and their respective versions will be available within the Parcels page.
4. Download, Distribute, Activate the required parcels to use them.

## Building the Parcel
1. Install [Docker](https://www.docker.com/) and [Python](https://www.python.org/).
2. Run the script `build_airflow_parcel.sh` by executing:
```bash
./build_airflow_parcel.sh --airflow <airflow_version> --python <python_version> --parcel <parcel_version>
```
3. Output will be placed in the target/ directory.
4. Use `./serve_parcel.sh` to serve this directory via HTTP, or move the entire directory contents to your own webserver.

## Resources:
1. https://github.com/teamclairvoyant/apache-airflow-csd

