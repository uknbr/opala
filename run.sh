#!/bin/bash
set -euo pipefail
BASEDIR=$(dirname "${BASH_SOURCE}")

wait_time=${DAEMON_INTERVAL:-15}
wait_time=$((wait_time * 60))
db_sync=${MYSQL_SYNC:-False}

while true ; do
	echo "[$(date +'%D %T')] Running in silent mode with parameters: ${CAR_MODEL} | ${CAR_REGION} | ${CAR_DATE_BEGIN} | ${CAR_DATE_END}"
	python3 ${BASEDIR}/car.py -q || true

	if [ "${db_sync}" == "True" ] ; then
		echo "[$(date +'%D %T')] Sync local data to MySQL (${MYSQL_HOST}:${MYSQL_PORT})"
		sqlite3mysql -f olx/db/car.db -d ${MYSQL_DATABASE} -h ${MYSQL_HOST} -P ${MYSQL_PORT} -u ${MYSQL_USER} --mysql-password ${MYSQL_PASS} -l olx/log/sync.log -q
	fi

	echo "[$(date +'%D %T')] Waiting ${wait_time} seconds for next execution"
	sleep ${wait_time}
done