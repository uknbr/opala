FROM python:3.7.0-alpine3.7

MAINTAINER "pedro.pavan@linuxmail.org"
LABEL github="https://github.com/uknbr"
LABEL platform="OLX"
LABEL items="car"

RUN apk add --no-cache --upgrade bash
RUN addgroup -S olx && adduser -S -G olx -h /home/car car
WORKDIR /home/car/app
COPY . /home/car/app
RUN chown -R car:olx /home/car/
USER car
RUN pip3 install -r requirements.txt --no-cache-dir --user --no-warn-script-location

CMD [ "bash","run.sh" ]