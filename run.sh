#!/bin/bash
set -euo pipefail
BASEDIR=$(dirname "${BASH_SOURCE}")

wait_time=${DAEMON_INTERVAL:-15}
wait_time=$((wait_time * 60))

while true ; do
	echo "[$(date +'%D %T')] Running in silent mode with parameters: ${CAR_MODEL} | ${CAR_REGION} | ${CAR_DATE_BEGIN} | ${CAR_DATE_END}"
	python3 ${BASEDIR}/car.py -r ${CAR_REGION} -b ${CAR_DATE_BEGIN} -e ${CAR_DATE_END} -q || true
	echo "[$(date +'%D %T')] Waiting ${wait_time} seconds for next execution"
	sleep ${wait_time}
done
