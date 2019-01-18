#!/bin/bash

cd target || exit 1
echo "Parcel repo available at $(hostname):8000"
python -m SimpleHTTPServer 8000
