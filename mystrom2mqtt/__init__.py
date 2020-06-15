"""myStrom to MQTT bridge."""
import argparse
import asyncio
import json
import logging
import socket
import sys
from uuid import uuid4

import toml
from netaddr import EUI, mac_unix_expanded

import uvicorn
from asyncio_mqtt import Client, MqttError
from fastapi import BackgroundTasks, FastAPI, Form, Request

logger = logging.getLogger("mystrom2mqtt")
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Location of the configuration file")
args = parser.parse_args()

app = FastAPI()

# Load the Home Assistant Add-on configuration if available, otherwise local configuration file
try:
    with open("/data/options.json") as json_file:
        config = json.load(json_file)["mqtt"]
except FileNotFoundError:
    config = toml.load(args.config if args.config is not None else "config.toml")[
        "mystrom2mqtt"
    ]

logger.debug("Used configuration: %s", config)

broker = config["broker"]
port = config["port"]
username = config["username"]
password = config["password"]

# Based on the current published API documentation
ACTION_MAPPER = {
    "1": "button_short_press",  # "single"
    "2": "button_double_press",  # "double",
    "3": "button_long_press",  # "long"
    "4": "touch",  # "touch"
    "5": "wheel",
    "6": "battery",
    "11": "wheel_final",
}

ACTION_TYPES = [
    "button_short_press",
    "button_long_press",
    "button_double_press",
    "touch",
]

SENSOR_TYPES = {"battery": "battery", "wheel": None}

detected_devices = []


@app.get("/devices")
async def devices():
    return {"devices": detected_devices}


@app.post("/")
async def root(
    *,
    mac: str = Form(...),
    name: str = Form(None),
    wheel: str = Form(None),
    action: str = Form(...),
    battery: str = Form(...),
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Handle a POST request."""
    logger.debug("Request received: %s", request.__dict__)
    mac_address = EUI(mac, dialect=mac_unix_expanded)
    sensor_values = {"wheel": wheel, "battery": battery}
    messages = []

    logger.debug("Received sensor values: %s", sensor_values)
    if not detected_devices:
        logger.debug("New device: %s", mac)
    logger.debug("Detected devices: %s", detected_devices)

    if mac in detected_devices:
        logger.debug(
            "Device already configured: %s, %s", mac_address, request.client.host
        )

        for sensor in SENSOR_TYPES:
            topic_sensor = f"mystrom2mqtt/{mac}/{sensor}/state"
            payload = sensor_values[sensor]
            messages.append(
                {"topic": topic_sensor, "payload": payload, "qos": 0, "retain": False}
            )
            logger.debug("Topic: %s, Payload: %s", topic_sensor, payload)

        try:
            received_action = ACTION_MAPPER[action]
            logger.debug("Received action: %s", received_action)
            payload = "ON"
            topic_device_trigger = f"mystrom2mqtt/{mac}/{received_action}"
            messages.append(
                {
                    "topic": topic_device_trigger,
                    "payload": payload,
                    "qos": 0,
                    "retain": False,
                }
            )
            logger.debug("Topic: %s, Payload: %s", topic_device_trigger, payload)
        except KeyError:
            logger.debug("Unknown action: %s", received_action)

        async with Client(
            broker,
            port=port,
            username=username,
            password=password,
            client_id=f"mystrom2mqtt-{uuid4()}",
        ) as client:
            for message in messages:
                await client.publish(
                    message["topic"],
                    message["payload"],
                    message["qos"],
                    message["retain"],
                )

        return

    if wheel is None:
        hardware_type = "Button"
    else:
        hardware_type = "Button+"

    device_data = {
        "identifiers": f"mystrom_{mac}",
        "connections": [["mac", str(mac_address)]],
        "model": f"myStrom {hardware_type}",
        "name": mac,
        "manufacturer": "myStrom AG",
        "via_device": "mystrom2mqtt",
    }

    for sensor_type in SENSOR_TYPES:
        logger.debug("Adding sensor: %s", sensor_type)

        config_topic_sensor = f"homeassistant/sensor/{mac}/{mac}_{sensor_type}/config"
        topic_sensor = f"mystrom2mqtt/{mac}/{sensor_type}/state"

        sensor_config_data = {
            "name": f"myStrom Wifi Button {sensor_type}",
            "state_topic": topic_sensor,
            "device_class": SENSOR_TYPES[sensor_type],
            "unique_id": f"{mac}_{sensor_type}_mystrom2mqtt",
            "device": device_data,
        }
        logger.debug(sensor_config_data)
        messages.append(
            {
                "topic": config_topic_sensor,
                "payload": json.dumps(sensor_config_data),
                "qos": 0,
                "retain": True,
            }
        )
        messages.append(
            {
                "topic": topic_sensor,
                "payload": sensor_values[sensor_type],
                "qos": 0,
                "retain": False,
            }
        )

    for action in ACTION_TYPES:
        logger.debug("Adding action: %s", action)
        config_topic_device_trigger = (
            f"homeassistant/device_automation/{mac}/{action}/config"
        )
        topic_device_trigger = f"mystrom2mqtt/{mac}/{action}"
        trigger_config_data = {
            "automation_type": "trigger",
            "type": action,
            "subtype": "button_1",
            "topic": topic_device_trigger,
            "payload": "ON",
            "device": device_data,
        }
        logger.debug(trigger_config_data)
        messages.append(
            {
                "topic": config_topic_device_trigger,
                "payload": json.dumps(trigger_config_data),
                "qos": 0,
                "retain": True,
            }
        )

    detected_devices.append(mac)

    async with Client(
        broker,
        port=port,
        username=username,
        password=password,
        client_id=f"mystrom2mqtt-{uuid4()}",
    ) as client:
        for message in messages:
            await client.publish(
                message["topic"], message["payload"], message["qos"], message["retain"]
            )


def run():
    """Run the gateway."""
    uvicorn.run(app, host="0.0.0.0", port=8321)
