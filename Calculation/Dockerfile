FROM ubuntu:latest

COPY calculation.py /

WORKDIR /

RUN apt update -y
RUN apt install -y python3 python3-pip

CMD python3 calculation.py

EXPOSE 4001
