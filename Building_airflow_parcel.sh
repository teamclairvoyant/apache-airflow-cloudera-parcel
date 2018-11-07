parcel_version=$1
airflow_version=$2
python_version=$3
airflow_parcel_name=AIRFLOW-${parcel_version}-${airflow_version}-${python_version}


os_ver=`cat /etc/os-release | grep VERSION_ID`

if [[ $os_ver == 'VERSION_ID="7"' ]]; then 
	dist_suff=el7; 
elif [[ $os_ver == 'VERSION_ID="6"' ]]; then 
	dist_suff=el6; 
else 
	echo "Unsupported operating system"; 
fi

mkdir -p ${airflow_parcel_name}/usr/bin
mkdir -p ${airflow_parcel_name}/usr/lib/python2.7/
mkdir -p ${airflow_parcel_name}/usr/include/

cp /usr/bin/*python* ${airflow_parcel_name}/usr/bin
cp /usr/bin/*airflow* ${airflow_parcel_name}/usr/bin
cp /usr/bin/*gunicorn* ${airflow_parcel_name}/usr/bin
cp -r /lib64/ ${airflow_parcel_name}/
cp -r /usr/lib/python2.7/site-packages ${airflow_parcel_name}/usr/lib/python2.7/
cp -r /usr/include/python2.7 ${airflow_parcel_name}/usr/include/

patchelf --version
exit_code="$?"

if [ $exit_code != 0 ] && [ $os_ver == 'VERSION_ID="7"' ]; then
        wget -P /tmp http://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/p/patchelf-0.9-9.el7.x86_64.rpm
        rpm -Uvh /tmp/patchelf-0.9-9.el7.x86_64.rpm
elif [ $exit_code != 0 ] && [ $os_ver == 'VERSION_ID="6"' ]; then
		wget -P /tmp http://dl.fedoraproject.org/pub/epel/6/x86_64/Packages/p/patchelf-0.9-9.el6.x86_64.rpm
		rpm -Uvh /tmp/patchelf-0.9-9.el6.x86_64.rpm
fi

cd ${airflow_parcel_name}/usr/bin
patchelf --set-rpath '../../lib64' ./python2.7

cd ../..

tar zcvf ${airflow_parcel_name}-${dist_suff}.parcel ${airflow_parcel_name}

sha1sum ${airflow_parcel_name}-${dist_suff}.parcel | awk '{ print $1 }' > $${airflow_parcel_name}-${dist_suff}.parcel.sha