FROM python:3.7.0-alpine3.7

MAINTAINER "pedro.pavan@linuxmail.org"
LABEL github="https://github.com/uknbr"
LABEL car="opala"
LABEL platform="OLX"

RUN apk add --no-cache --upgrade bash
RUN addgroup -S car && adduser -S -G car -h /home/opala opala
WORKDIR /home/opala/app
COPY . /home/opala/app
RUN chown -R opala:car /home/opala/
USER opala
RUN pip3 install -r requirements.txt --no-cache-dir --user --no-warn-script-location

CMD [ "bash","run.sh" ]