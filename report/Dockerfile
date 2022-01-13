FROM golang:1.17.6-alpine as build_img
RUN apk add --no-cache git
WORKDIR /output/
COPY . .
RUN go mod download
RUN go build -o /output/olx-report .

FROM alpine:3.15.0
WORKDIR /app
COPY --from=build_img /output/olx-report /app/olx-report