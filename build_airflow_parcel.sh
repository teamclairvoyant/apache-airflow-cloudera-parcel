parcel_version=$1
airflow_version=$2
python_version=$3
airflow_parcel_name=AIRFLOW-${parcel_version}-${airflow_version}-${python_version}
cur_working_dir=`pwd`
full_path=${cur_working_dir}/${airflow_parcel_name}

os_ver=`cat /etc/os-release | grep VERSION_ID`

if [[ $os_ver == 'VERSION_ID="7"' ]]; then 
	dist_suffix=el7; 
elif [[ $os_ver == 'VERSION_ID="6"' ]]; then 
	dist_suffix=el6; 
else 
	echo "Unsupported operating system"; 
fi

YUMOPTS="-y -e1 -d1"
yum $YUMOPTS groupinstall -y "development tools"
yum $YUMOPTS install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel
yum $YUMOPTS install -y wget
yum $YUMOPTS install mysql-devel
yum $YUMOPTS install postgresql-devel

mkdir -p ${full_path}

wget http://python.org/ftp/python/${python_version}/Python-${python_version}.tar.xz
tar xf Python-${python_version}.tar.xz
cd Python-${python_version}
./configure --prefix=${full_path}
make && make altinstall
cd ${cur_working_dir}

wget -P /tmp wget https://bootstrap.pypa.io/get-pip.py
${full_path}/bin/python2.7 /tmp/get-pip.py

${full_path}/bin/pip $PIPOPTS install airflow==${airflow_version}
${full_path}/bin/pip $PIPOPTS install 'celery<4'
${full_path}/bin/pip $PIPOPTS install airflow[celery]
${full_path}/bin/pip $PIPOPTS install airflow[mysql]
${full_path}/bin/pip $PIPOPTS install airflow[postgres]
${full_path}/bin/pip $PIPOPTS install airflow[kerberos]
${full_path}/bin/pip $PIPOPTS install airflow[crypto]
${full_path}/bin/pip $PIPOPTS install airflow[hive]
${full_path}/bin/pip $PIPOPTS install airflow[password]
${full_path}/bin/pip $PIPOPTS install airflow[rabbitmq]

cp -rf meta ${airflow_parcel_name}/

sed -i "4s/.*/  \"version\": \"${PARCEL_NAME}\",/" ${parcel_version}-${airflow_version}-${python_version}/meta/parcel.json

tar zcvf ${airflow_parcel_name}-${dist_suffix}.parcel ${airflow_parcel_name}

sha1sum ${airflow_parcel_name}-${dist_suffix}.parcel | awk '{ print $1 }' > ${airflow_parcel_name}-${dist_suffix}.parcel.sha