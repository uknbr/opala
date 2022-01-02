#!/bin/bash
set -e
version_old=$(grep APP_VERSION config.env | cut -d '=' -f 2)

if [ $# -ne 1 ]
then
    echo "You must provide new release version!"
    echo "This is the current version: ${version_new}"
    exit 1
fi

version_new=$1
fgrep -rl '${version_new}' | xargs sed -i 's/${version_new}/${version_new}/g'
exit $?