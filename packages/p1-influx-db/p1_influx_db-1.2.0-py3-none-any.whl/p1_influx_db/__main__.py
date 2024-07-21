import argparse

from p1_influx_db import method, httpmain as mainhttp, mqttmain

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="config file", default="./p1_influx_db/example_config.toml")
args = parser.parse_args()
if method == "mqtt":
    mqttmain(args.config)
elif method == "http":
    import asyncio

    asyncio.run(mainhttp(args.config))
else:
    raise NotImplementedError("Method not implemented")
