FROM golang:1.17.1-alpine as build_img
RUN apk add --no-cache git
WORKDIR /output/
COPY go.mod .
RUN go mod download
COPY main.go .
RUN go build -o /output/main .

FROM alpine:3.9 
WORKDIR /app
COPY --from=build_img /output/main /app/main