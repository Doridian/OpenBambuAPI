# Basics

All messages on the MQTT broker are JSON encoded

There is two ways to connect to the MQTT broker

## Cloud MQTT server

URL: `mqtt://us.mqtt.bambulab.com:8883`

TLS: **yes**

Authentication: **required**

**Username:** `u_{USER_ID}`, where the user id can be grabbed by cracking your own `{ACCESS_TOKEN}` (which is a JWT) and reading its `preferred_username` field.

**Password:** `{ACCESS_TOKEN}` (the entire JWT, no prefix or suffix)

## Local MQTT server

URL: `mqtt://{PRINTER_IP}:1883`

TLS: **no**

Authentication: **disabled**

Wildcard subscriptions with `#` possible

# Topics

## device/{DEVICE_ID}/report

For information from the device to the slicer, including responses to commands

## device/{DEVICE_ID}/request

For commands to the device from the slicer

The command structure is currently unknown
