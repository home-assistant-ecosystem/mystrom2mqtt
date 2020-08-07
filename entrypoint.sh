#!/bin/bash

# Create config file if not mapped
if [ ! -r /app/config.toml ]
then
	cat > /app/config.toml << EOF
[mystrom2mqtt]
broker = "${BROKER:-localhost}"
port = ${PORT:-1883}
username = "${USERNAME:-}"
password = "${PASSWORD:-}"
EOF
fi

exec mystrom2mqtt --config /app/config.toml
