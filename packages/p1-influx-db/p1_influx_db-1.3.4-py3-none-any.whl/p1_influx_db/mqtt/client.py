import paho.mqtt.client as mqtt
from loguru import logger
import ssl

from p1_influx_db.dsmr_parse import dsmrMessages


class MqttClient(mqtt.Client):
    def __init__(self, broker, port, client_id, ca_certs, certfile, key):
        super().__init__(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.tls_set(
            ca_certs=ca_certs,
            certfile=certfile,
            keyfile=key,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
        )

    def on_connect(self, userdata, flags, rc, properties):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
        else:
            logger.error("Failed to connect, return code %d\n", rc)

    def on_publish(self, userdata, mid, reason_code, properties):
        try:
            userdata.remove(mid)
        except KeyError:
            logger.error("Race condition occured as such mid is missing")

    def start(self):
        self.connect(self.broker, self.port)
        self.loop_start()

    def stop(self):
        self.loop_stop()

    def publish(self, message: dsmrMessages):
        topic = message["topic"]
        payload = message["payload"]
        result = self.publish(topic, payload)

        status = result[0]
        if status == 0:
            logger.debug(f"Send `{payload}` to topic `{topic}`")
        else:
            logger.error(f"Failed to send message to topic {topic}")
