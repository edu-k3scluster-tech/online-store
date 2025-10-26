FROM python:3.12

WORKDIR /app

COPY requirements.txt ./
COPY app/ /order/src/
#COPY bin/ /order/bin/

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000

WORKDIR /order
ENV PYTHONPATH /order/src:/order