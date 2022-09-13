# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

COPY requirements.txt app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

WORKDIR /app/src

RUN python3 create_db.py

RUN python3 add_user.py

ENTRYPOINT ["python3"]

CMD ["softdes.py"]