import json
import os
import ssl
from typing import Any, Union

import paho.mqtt.client as mqtt


def create_local_ssl_context() -> ssl.SSLContext:
    """
    This context validates the certificate for TLS connections to local printers.
    It additionally requires calling `context.wrap_socket(sock, servername=device_serial_number)`
    for the Server Name Indication (SNI).
    """
    context = ssl.create_default_context(cafile="ca_cert.pem")
    context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return context


class MQTTSClient(mqtt.Client):
    """
    MQTT Client that supports custom certificate Server Name Indication (SNI) for TLS.
    see https://github.com/eclipse-paho/paho.mqtt.python/issues/734#issuecomment-2256633060
    """

    def __init__(self, *args, server_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._server_name = server_name

    def _ssl_wrap_socket(self, tcp_sock) -> ssl.SSLSocket:
        orig_host = self._host
        if self._server_name:
            self._host = self._server_name
        res = super()._ssl_wrap_socket(tcp_sock)
        self._host = orig_host
        return res


def connect_local_mqtt(hostname: str, device_id: str, access_code: str) -> mqtt.Client:
    client = MQTTSClient(mqtt.CallbackAPIVersion.VERSION2, server_name=device_id)
    client.tls_set_context(create_local_ssl_context())
    client.username_pw_set("bblp", access_code)
    client.connect(hostname, port=8883, keepalive=60)
    return client


def connect_cloud_mqtt(username: str, access_token: str) -> mqtt.Client:
    client = MQTTSClient(mqtt.CallbackAPIVersion.VERSION2)
    client.tls_set()
    client.username_pw_set(username, access_token)
    client.connect("us.mqtt.bambulab.com", port=8883, keepalive=60)
    return client


def on_connect(
    client: mqtt.Client,
    userdata: Any,
    flags: mqtt.ConnectFlags,
    reason_code: mqtt.ReasonCode,
    properties: Union[mqtt.Properties, None],
):
    print(f"Connected with result code {reason_code}")
    client.publish(
        f"device/{DEVICE_ID}/request",
        json.dumps(
            {
                "system": {
                    "sequence_id": 0,
                    "command": "ledctrl",
                    "led_node": "chamber_light",
                    "led_mode": "on",
                }
            }
        ),
    )


def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
    print(msg.topic + " " + str(msg.payload))


HOSTNAME = os.getenv("DEVICE_HOSTNAME")
DEVICE_ID = os.getenv("DEVICE_ID")
ACCESS_CODE = os.getenv("DEVICE_ACCESS_CODE")

# USERNAME = os.getenv("USERNAME")
# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


if __name__ == "__main__":
    client = connect_local_mqtt(HOSTNAME, DEVICE_ID, ACCESS_CODE)
    # client = connect_cloud_mqtt(USERNAME, ACCESS_TOKEN)

    client.subscribe(f"device/{DEVICE_ID}/report")
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
