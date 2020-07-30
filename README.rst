myStrom2MQTT
============

`myStrom <https://mystrom.ch>`_ buttons allows to send HTTP requests. If a press
pattern is applied then a request is send to a devices. 

This module is not official, developed, supported or endorsed by myStrom AG.

For questions and other inquiries, use the issue tracker in this repository please.

myStrom AG has provided and is still providing hardware for testing and development.

Supported home automation platforms
-----------------------------------

Add the moment the following platforms are supported:

- `Home Assistant <https://home-assistant.io>`_

Requirements
------------

You need to have `Python <https://www.python.org>`_ installed.

- `myStrom <https://mystrom.ch>`_ button (button or button+, could work with the Motion sensor too)
- A MQTT broker
- Network connection
- Devices connected to your network

Non-Docker deployment
---------------------

Installation 
~~~~~~~~~~~~

The package is available in the `Python Package Index <https://pypi.python.org/>`_ .

.. code:: bash

    $ pip3 install mystrom2mqtt

Usage
~~~~~

Set the target of the button. The port which is used by ``mystrom2mqtt`` is 8321.

.. code:: bash

   curl --location --request POST 'http://[IP of the button]/api/v1/action/generic' \
     --data-raw 'post://[mystrom2mqtt host]:8321'

A configuration file is needed. The format is TOML and the default name ``config.toml``.

.. code:: bash

   [mystrom2mqtt]
   broker = "192.168.0.20"
   port = 1883
   username = "mqtt"
   password = "mqtt"

To start ```mystrom2mqtt`` specify the path with ``--config`` to the configuration
file:

.. code:: bash

   mystrom2mqtt --config path/to/config.toml


To autostart ``mystrom2mqtt`` create a systemd unit file named ``/etc/systemd/system/mystrom2mqtt.service``
with the parameters you 

.. code:: bash

   [Unit]
   Description=myStrom2MQTT
   After=network-online.target
   
   [Service]
   Type=simple
   ExecStart=/usr/bin/mystrom2mqtt --config "/path/to/config.toml"
   
   [Install]
   WantedBy=multi-user.target

Docker deployment
-----------------

Installation
~~~~~~~~~~~~

Create the docker image either with docker 

.. code:: bash

    $ docker build -t mystrom2mqtt:1 .

Usage
~~~~~

The configuration is needed either using docker environments or config file. The
following variables are processed:


+--------------+---------------------------------------+
| Variable     |                                       |
+--------------+---------------------------------------+
| ``BROKER``   | The address or name of the broker.    |
+--------------+---------------------------------------+
| ``PORT``     | The port or the broker. Default 1883. |
+--------------+---------------------------------------+
| ``USERNAME`` | The username. Default no user.        |
+--------------+---------------------------------------+
| ``PASSWORD`` | The password. Default no password.    |
+--------------+---------------------------------------+

Example:

.. code:: bash
    $ docker run -e BROKER=192.168.1.1 -p 8321:8321 mystrom2mqtt:1

With config file instead of variables:

.. code:: bash
    $ docker run -v ./config.toml:/app/config.toml -p 8321:8321 mystrom2mqtt:1


License
-------

``mystrom2mqtt`` is licensed under ASL 2.0, for more details check LICENSE.
