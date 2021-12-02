#!/bin/bash

### PARAM
file="olx-full-backup-$(date +%s).sql"
folder="${HOME}/opala/olx/db"
keep=7

### BACKUP
mkdir -p ${folder}
docker exec dashboard_mysql_1 sh -c 'exec mysqldump --all-databases --no-tablespaces --single-transaction --quick --lock-tables=false -ucar -pOlx@123' > ${folder}/${file}

### COMPACT
if [ $? -eq 0 ] ; then
    gzip -9 ${folder}/${file}
fi

### OLD DATA
find ${folder}/ -type f -name '*.sql' -delete
find ${folder}/ -type f -name '*.gz' -mtime +${keep} -delete

exit 0