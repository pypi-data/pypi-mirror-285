from datetime import datetime
from dateutil.relativedelta import relativedelta

from brevo_dc_cli.helper.datacontract_helper import (
    generate_datacontract,
    diff_datacontract,
    publish_datacontract,
)



def datacontract_generate(module: str, service: str, verbose: bool, args: str):
    generate_datacontract(*args)


def datacontract_diff(module: str, service: str, verbose: bool, args: str):
    diff_datacontract(args[0])


def datacontract_publish(module: str, service: str, verbose: bool, args: str):
    publish_datacontract(args[0])


def datacontract_all(module: str, service: str, verbose: bool, args: str):
    generate_datacontract(*args)
    publish_datacontract(args[2])
