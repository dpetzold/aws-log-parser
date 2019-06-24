from python:3.7-alpine

WORKDIR /tmp
RUN wget --quiet https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz \
    && tar xvfz GeoLite2-Country.tar.gz \
    && mv GeoLite2-Country_*/*.mmdb /app

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["/usr/arc/app/bin/aws-log-parser"]
