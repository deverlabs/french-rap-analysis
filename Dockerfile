FROM python:3.7.2

RUN mkdir -p /app
WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     rsync

# COPY . .

# RUN pip install -e .