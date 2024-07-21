import influxdb_client
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from aiohttp.client_exceptions import ClientConnectorError

from loguru import logger
import asyncio


async def send_parsed_telegram(info_list, queue: asyncio.Queue, config_file: str):
    logger.info("Opening InfluxDBClient")
    async with InfluxDBClientAsync.from_config_file(config_file) as client:
        logger.info("Writing to influxdb")
        write_api = client.write_api()
        writetasks = []
        for item in info_list:
            writetasks.append(write_api.write(bucket=item[0], record=influxdb_client.Point.from_dict(item[1])))

        results = await asyncio.gather(*writetasks, return_exceptions=True)
        for bucket_info, result in enumerate(zip(info_list, results)):
            if isinstance(result, ClientConnectorError):
                logger.error(f"Error connecting to influxdb: {result}")
                raise result
            elif isinstance(result, Exception):
                logger.error(f"Error writing to bucket {bucket_info[0]}: {result.with_traceback()}")
                raise result
            else:
                logger.info(f"Writing to bucket {result[0][0]} succeeded")
        return results
