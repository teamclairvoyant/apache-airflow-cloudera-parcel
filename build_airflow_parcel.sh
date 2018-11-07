parcel_version=$1
airflow_version=$2
python_version=$3
airflow_parcel_name=AIRFLOW-${parcel_version}-${airflow_version}-${python_version}
full_path=`pwd`/${airflow_parcel_name}

# yum groupinstall -y "development tools"
# echo "installed development tools"
# exit 1
# yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel
# yum install -y wget

if [ $python_version == "2.7.14" ];then
	wget http://python.org/ftp/python/2.7.14/Python-2.7.14.tar.xz
	tar xf Python-2.7.14.tar.xz
	cd Python-2.7.14
	echo "full_path is ${full_path}"
	./configure --prefix=${full_path}
	make && make altinstall
	cd ..
fi

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

tar zcvf ${airflow_parcel_name}-el7.parcel ${airflow_parcel_name}

sha1sum ${airflow_parcel_name}-el7.parcel | awk '{ print $1 }' > ${airflow_parcel_name}-el7.parcel.sha
