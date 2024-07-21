from loguru import logger
import toml
import asyncio

from dsmr_parser import telegram_specifications
from dsmr_parser.clients import AsyncSerialReader, SERIAL_SETTINGS_V5
from .dsmr_parse import parse_dsmr_telegram
from aiohttp.client_exceptions import ClientConnectorError


async def parse_telegram_influx(name, queue: asyncio.Queue, config_file: str):
    while True:
        telegram = await queue.get()
        info_list = parse_dsmr_telegram(telegram)
        from .http_to_influxdb import send_parsed_telegram

        results = await send_parsed_telegram(info_list, queue, config_file)
        queue.task_done()


async def httpmain(config_file="./p1_influx_db/config.toml"):
    queue = asyncio.Queue()
    with open(config_file, "r") as f:
        config = toml.load(f)
    logger.info("Opening SerialReader")
    serial_reader = AsyncSerialReader(
        device=config["p1"]["device"],
        serial_settings=SERIAL_SETTINGS_V5,
        telegram_specification=telegram_specifications.V5,
    )
    tasks = []
    for i in range(3):
        tasks.append(asyncio.create_task(parse_telegram_influx(f"worker-{i}", queue, config_file=config_file)))

    await serial_reader.read_as_object(queue)
    result = await asyncio.gather(*tasks, return_exceptions=True)
    for r in result:
        if isinstance(r, ClientConnectorError):
            raise r
        elif isinstance(r, Exception):
            raise r
