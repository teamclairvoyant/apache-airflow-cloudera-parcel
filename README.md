# Airflow [Parcel](https://github.com/cloudera/cm_ext/wiki/Parcels:-What-and-Why%3F)

This repository allows you to install [Apache Airflow](https://airflow.apache.org/) as a parcel deployable by [Cloudera Manager](https://www.cloudera.com/products/product-components/cloudera-manager.html).

## Usage
### With Airflow CSD:
1. Install the [Airflow CSD](https://github.com/teamclairvoyant/apache-airflow-cloudera-csd).  
1. In Cloudera Manager, go to `Hosts -> Parcels`:
    1. Check for new packages, and wait a few minuets
    1. Airflow parcels and their respective versions will be available within the Parcels page
1. Download, Distribute, Activate the required parcels to use them

### With Self-Built:
1. Follow [build steps](#build-steps)
1. In Cloudera Manager, go to `Hosts -> Parcels`:
    1. Under `Configuration` add `http://LINK TO YOUR REPO/`to the Remote Parcel Repository URLs if it does not yet exist
    1. Check for new packages, and wait a few minuets
    1. Airflow parcels and their respective versions will be available within the Parcels page
1. Download, Distribute, Activate the required parcels to use them

### Troubleshooting
| Issue | solution |
| --- | --- |
|The parcels don't appear with under `Hosts -> Parcels` with the CSD installed |**Manually specify the Remote Parcel Repository:**<br>1. In Cloudera Manager, go to `Hosts -> Parcels -> Configuration`.<br>2. Add `http://archive.clairvoyantsoft.com/airflow/parcels/latest/` to the Remote Parcel Repository URLs.<br>3. Check for new parcels and wait a few minuets. |


## Building
### Build Steps:
1. Install [Docker](https://www.docker.com/) and [Python](https://www.python.org/).
1. Run the script `build_airflow_parcel.sh` by executing:
    1. `./build_airflow_parcel.sh --airflow <airflow_version> --python <python_version> --parcel <parcel_version> [--dist <distro>]`
1. Output will be placed in the `target/` directory
1. Serve the `target/` directory via HTTP:
    1. Use `./serve_parcel.sh` to serve this directory via HTTP
    1. OR:: move the entire directory contents to your own web server

### Support Matrix:
| DISTRO | AIRFLOW_VERSION | PYTHON_VERSION |
| --- | --- | --- |
| centos6 / rhel6 | `1.10.3+` | `3.5+` & `<3.7` |
| centos7 / rhel7 | `1.10.3+` | `3.5+` |
| debian8 | `1.10.3+` | `3.5+` |
| ubuntu1404 | `1.10.3+`  | `3.5+` |
| ubuntu1604 | `1.10.3+`  | `3.5+` |
| ubuntu1804 | `1.10.3+`  | `3.5+` |