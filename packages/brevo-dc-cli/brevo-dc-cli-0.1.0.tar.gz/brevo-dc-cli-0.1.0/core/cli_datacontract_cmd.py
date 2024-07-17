from datetime import datetime
from dateutil.relativedelta import relativedelta

from core.helper.datacontract_helper import (
    generate_datacontract,
    diff_datacontract,
    publish_datacontract,
)


periode = (datetime.now() - relativedelta(months=0, days=1)).strftime("%Y-%m-%d")


def datacontract_generate(module: str, service: str, verbose: bool, args: str):
    generate_datacontract(*args, periode)


def datacontract_diff(module: str, service: str, verbose: bool, args: str):
    diff_datacontract(args[0])


def datacontract_publish(module: str, service: str, verbose: bool, args: str):
    publish_datacontract(args[0])


def datacontract_all(module: str, service: str, verbose: bool, args: str):
    generate_datacontract(*args, periode)
    publish_datacontract(args[2])
