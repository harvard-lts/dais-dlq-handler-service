FROM python:3.10.2-slim
COPY requirements.txt /tmp/

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y vim libpq-dev gcc supervisor python3-pip openssl nginx curl && \
    mkdir -p /etc/nginx/ssl/ && \
    openssl req \
            -x509 \
            -subj "/C=US/ST=Massachusetts/L=Cambridge/O=Dis" \
            -nodes \
            -days 365 \
            -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/nginx.key \
            #-addext "subjectAltName=DNS:localhost" \
            -out /etc/nginx/ssl/nginx.cert && \
    chmod -R 755 /etc/nginx/ssl/ && \
    pip install --upgrade pip && \
    pip install gunicorn && \
    pip install -r /tmp/requirements.txt -i https://pypi.org/simple/ --extra-index-url https://test.pypi.org/simple/ && \
    groupadd -r -g 55020 hdhsuser && \
    useradd -u 55020 -g 55020 --create-home hdhsuser

# Install git, required for GitPython
RUN apt-get install -y git

WORKDIR /home/hdhsuser

# Copy code into the image
COPY --chown=hdhsuser . /home/hdhsuser

RUN rm -f /etc/nginx/sites-enabled/default && \
    rm -f /etc/service/nginx/down && \
    mkdir -p /data/nginx/cache && \
    mv /home/hdhsuser/webapp.conf.example /etc/nginx/conf.d/webapp.conf && \
    chown hdhsuser /etc/ssl/certs && \
    chown hdhsuser /etc/ssl/openssl.cnf && \
    chown -R hdhsuser /var/log/nginx && \
    chown -R hdhsuser /var/lib/nginx && \
    chown -R hdhsuser /data && \
    chown -R hdhsuser /run

WORKDIR /home/hdhsuser

# Supervisor to run and manage multiple apps in the same container
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

USER hdhsuser

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
