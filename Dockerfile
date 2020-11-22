FROM python:3.7.0-alpine3.7

MAINTAINER "pedro.pavan@linuxmail.org"
LABEL github="https://github.com/uknbr"
LABEL platform="OLX"
LABEL items="car"

RUN pip3 install --upgrade pip && pip3 install sqlite3-to-mysql

RUN apk add --no-cache --upgrade bash
RUN addgroup -g 222 -S olx && adduser -u 222 -S -G olx -h /home/car car
WORKDIR /home/car/app
COPY . /home/car/app
RUN mkdir -p /home/car/data && chown -R car:olx /home/car/
USER car
RUN pip3 install -r requirements.txt --no-cache-dir --user --no-warn-script-location

HEALTHCHECK --interval=10s --timeout=2s CMD pgrep -f run.sh || exit 1
CMD [ "bash","run.sh" ]