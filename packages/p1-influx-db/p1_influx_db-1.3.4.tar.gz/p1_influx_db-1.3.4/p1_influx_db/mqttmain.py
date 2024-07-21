from loguru import logger
import toml

from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V5


from p1_influx_db.mqtt import Client
from p1_influx_db.dsmr_parse import parse_dsmr_telegram


def mqttmain(config_file="./p1_influx_db/example_config.toml"):
    logger.info("Opening SerialReader")
    with open(config_file, "r") as f:
        config = toml.load(f)
        mqtt_config = config["mqtt"]

    client = Client(**mqtt_config)
    client.start()
    serial_reader = SerialReader(
        device=config["p1"]["device"],
        serial_settings=SERIAL_SETTINGS_V5,
        telegram_specification=telegram_specifications.V5,
    )
    try:
        for telegram in serial_reader.read_as_object():
            info_list = parse_dsmr_telegram(telegram)

            for dsmr_message in info_list:
                client.publish(dsmr_message)
    except Exception as e:
        client.stop()
        logger.info("Closing MqttClient")
        raise e
