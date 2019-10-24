FROM python:3.7-alpine


RUN apk --update add git \
    && rm -rf /var/lib/apt/lists/* \
    && rm /var/cache/apk/*

WORKDIR /tmp

RUN mkdir -p /usr/src/app \
    && wget --quiet https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz \
    && tar xvfz GeoLite2-Country.tar.gz \
    && mv GeoLite2-Country_*/*.mmdb /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
