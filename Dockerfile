FROM python:3.8

# Pre-Install depedencies for faster rebuild of image
RUN pip install \
	python-multipart \
	fastapi \
	uvicorn \
	toml \
	netaddr \
	asyncio_mqtt

ADD ["setup.py", "README.rst", "/app/lib/mystrom2mqtt/"]
ADD mystrom2mqtt /app/lib/mystrom2mqtt/mystrom2mqtt/

RUN pip install -e /app/lib/mystrom2mqtt/

EXPOSE 8321/tcp
VOLUME /app/

ADD entrypoint.sh /app/

ENTRYPOINT ["/app/entrypoint.sh"]

