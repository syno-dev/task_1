FROM ubuntu:latest

ENV CAL_HOST calculation
ENV DB /DB/simple_db.db

COPY DB /DB
COPY api.py /
COPY requirements.txt /

WORKDIR /

RUN apt update -y
RUN apt install -y python3 python3-pip
RUN pip3 install -r requirements.txt

CMD python3 api.py


EXPOSE 4000
