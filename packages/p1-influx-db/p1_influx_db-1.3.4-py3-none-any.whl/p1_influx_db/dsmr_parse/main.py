from loguru import logger
from typing import Dict, List

from dsmr_parser.objects import Telegram

import json

from .formats import dsmrMessages, p1Messages


def fill_fields(
    parsed_telegram: Dict[str, any],
    keylist: List[str],
    message: p1Messages,
    p1MessageList: List[p1Messages],
    unitCheck: str,
    topic: str,
):
    """
    Fill the fields of the message with values from the parsed telegram.

    Args:
        parsed_telegram (Dict[str, any]): The parsed telegram containing key-value pairs.
        keylist (List[str]): The list of keys to be filled in the message fields.
        message (p1Messages): The message object to be filled.
        p1MessageList (List[p1Messages]): The list of message objects.

    Returns:
        List[p1Messages]: The updated list of message objects.
    """
    message = message.model_dump()
    for key in keylist:
        if key not in parsed_telegram:
            logger.error("Key not in telegram")
            continue
        if parsed_telegram[key]["unit"] != unitCheck:
            logger.critical(f"Unit is not {unitCheck}")
            return p1MessageList
        message["fields"][key.lower()] = parsed_telegram[key]["value"]
    if list(dict(message)["fields"].keys()):
        p1MessageList.append(dsmrMessages(topic=topic, payload=p1Messages(**message)))
    return p1MessageList


def parse_dsmr_telegram(telegram: Telegram):
    """
    Parses a DSMR telegram and returns a list of dsmrMessages.

    Args:
        telegram (Telegram): The DSMR telegram to parse.

    Returns:
        list: A list of dsmrMessages containing the parsed data.

    """
    logger.info("Data to write:")
    p1MessageList = []
    electricity_measurement = p1Messages(
        measurement="electricity",
        tags={
            "unit": "kWh",
            "equipment_id": telegram["EQUIPMENT_IDENTIFIER"]["value"],
        },
        fields={},
        time=telegram["P1_MESSAGE_TIMESTAMP"]["value"],
    )
    p1MessageList = fill_fields(
        telegram,
        [
            "ELECTRICITY_USED_TARIFF_1",
            "ELECTRICITY_USED_TARIFF_2",
            "ELECTRICITY_DELIVERED_TARIFF_1",
            "ELECTRICITY_DELIVERED_TARIFF_2",
        ],
        electricity_measurement,
        p1MessageList,
        "kWh",
        "latest_energy",
    )

    electricity_flow = p1Messages(
        measurement="electricity_current",
        tags={
            "unit": "kW",
            "actief_tarief": telegram["ELECTRICITY_ACTIVE_TARIFF"]["value"],
            "equipment_id": telegram["EQUIPMENT_IDENTIFIER"]["value"],
        },
        fields={},
        time=telegram["P1_MESSAGE_TIMESTAMP"]["value"],
    )
    p1MessageList = fill_fields(
        telegram,
        [
            "CURRENT_ELECTRICITY_USAGE",
            "CURRENT_ELECTRICITY_DELIVERY",
            "INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE",
            "INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE",
            "INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE",
            "INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE",
            "INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE",
            "INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE",
        ],
        electricity_flow,
        p1MessageList,
        "kW",
        "latest_energy_current",
    )

    voltages = p1Messages(
        measurement="voltage",
        tags={
            "unit": "V",
            "equipment_id": telegram["EQUIPMENT_IDENTIFIER"]["value"],
        },
        fields={},
        time=telegram["P1_MESSAGE_TIMESTAMP"]["value"],
    )
    p1MessageList = fill_fields(
        telegram,
        [
            "INSTANTANEOUS_VOLTAGE_L1",
            "INSTANTANEOUS_VOLTAGE_L2",
            "INSTANTANEOUS_VOLTAGE_L3",
        ],
        voltages,
        p1MessageList,
        "V",
        "latest_voltage_current",
    )
    currents = p1Messages(
        measurement="current",
        tags={
            "unit": "A",
            "equipment_id": telegram["EQUIPMENT_IDENTIFIER"]["value"],
        },
        fields={},
        time=telegram["P1_MESSAGE_TIMESTAMP"]["value"],
    )
    p1MessageList = fill_fields(
        telegram,
        [
            "INSTANTANEOUS_CURRENT_L1",
            "INSTANTANEOUS_CURRENT_L2",
            "INSTANTANEOUS_CURRENT_L3",
        ],
        currents,
        p1MessageList,
        "A",
        "latest_voltage_current",
    )

    gas = p1Messages(
        measurement="gas",
        tags={
            "unit": "m3",
            "equipment_id": telegram["EQUIPMENT_IDENTIFIER_GAS"]["value"],
        },
        fields={},
        time=telegram["P1_MESSAGE_TIMESTAMP"]["value"],
    )
    p1MessageList = fill_fields(
        telegram,
        ["HOURLY_GAS_METER_READING"],
        gas,
        p1MessageList,
        "m3",
        "latest_gas",
    )
    return p1MessageList
