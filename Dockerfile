FROM python:3.8-alpine

LABEL author="pedro.pavan@linuxmail.org"
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

CMD [ "bash","run.sh" ]