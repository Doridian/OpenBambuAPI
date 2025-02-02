import ssl

import paho.mqtt.client as mqtt


def create_local_ssl_context():
    """
    This context validates the certificate for TLS connections to local printers.
    It additionally requires calling `context.wrap_socket(sock, servername=printer_serial_number)`
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


def connect_local_mqtt(hostname, device_id, access_code):
    client = MQTTSClient(server_name=device_id)
    client.tls_set_context(create_local_ssl_context())
    client.username_pw_set("bblp", access_code)
    client.connect(hostname, port=8883, keepalive=60)
    return client


def connect_cloud_mqtt(username, access_token):
    client = MQTTSClient()
    client.tls_set()
    client.username_pw_set(username, access_token)
    client.connect("us.mqtt.bambulab.com", port=8883, keepalive=60)
    return client
