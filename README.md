

## Installing the Parcels
1. In the Cloudera Manager, go to `Hosts -> Parcels -> Configurations`.
2. Add `http://teamclairvoyant.s3-website-us-west-2.amazonaws.com/apache-airflow/cloudera/parcels/` to the Remote Parcel Repository URLs.
3. Airflow parcels and their respective verisons will be availble within the parcels page. 
4. Download, Distribute, Activate the required parcels to use them. 


## Building the parcel
1. Install the Airflow according to `https://airflow.apache.org/installation.html`.
2. Run the script `Building_airflow_parcel.sh` by executing 
```
	Building_airflow_parcel.sh <parcel_version> <airflow_version> <python_version>
```
3. A `.parcel` and a '.sha' file will be generated which can be used to generate the manifest.json and host it in repository.
