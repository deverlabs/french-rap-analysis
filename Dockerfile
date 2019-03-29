FROM python:3.7.2

RUN mkdir -p /app
WORKDIR /app

RUN pip install requests \
                bs4 \
                python-dotenv

# RUN apt-get update && apt-get install -y \
#     rsync

# COPY . .

# RUN pip install -e .