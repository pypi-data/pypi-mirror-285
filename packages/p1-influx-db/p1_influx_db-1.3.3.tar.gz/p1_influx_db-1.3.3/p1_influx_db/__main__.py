import argparse

from p1_influx_db import method

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="config file", default="./p1_influx_db/example_config.toml")
args = parser.parse_args()
if method == "mqtt":
    from p1_influx_db.mqttmain import mqttmain

    mqttmain(args.config)
elif method == "http":
    import asyncio
    from p1_influx_db.httpmain import httpmain as mainhttp

    asyncio.run(mainhttp(args.config))
else:
    raise NotImplementedError("Method not implemented")
