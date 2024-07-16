from core.helper.datacontract_helper import (
    generate_datacontract,
    diff_datacontract,
    publish_datacontract,
)

projet, raw_dataset, data_column, date_column, periode = (
    "root-station-198710",
    "raw_zone_airbyte",
    "_airbyte_data",
    "_airbyte_extracted_at",
    "2024-01-01",
)


def datacontract_generate(module: str, service: str, verbose: bool, args: str):
    raw_table_id = args[0]
    generate_datacontract(
        projet, raw_dataset, data_column, date_column, periode, raw_table_id
    )


def datacontract_diff(module: str, service: str, verbose: bool, args: str):
    diff_datacontract()


def datacontract_publish(module: str, service: str, verbose: bool, args: str):
    publish_datacontract()


def datacontract_all(module: str, service: str, verbose: bool, args: str):
    raw_table_id = args[0]
    generate_datacontract(
        projet, raw_dataset, data_column, date_column, periode, raw_table_id
    )
    publish_datacontract()
