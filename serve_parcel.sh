#!/bin/bash

cd target
echo Parcel repo available at `hostname`:8000
python -m SimpleHTTPServer 8000
