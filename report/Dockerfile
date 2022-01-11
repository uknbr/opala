FROM golang:1.17.1-alpine as build_img
RUN apk add --no-cache git
WORKDIR /output/
COPY . .
RUN go mod download
RUN go build -o /output/olx-report .

FROM alpine:3.9 
WORKDIR /app
COPY --from=build_img /output/olx-report /app/olx-report