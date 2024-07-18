import requests
import subprocess
from datacontract.data_contract import DataContract
from datacontract.cli import publish
import yaml, os, json
from rich.console import Console
from core.helper.secret_manager_helper import SecretManagerHelper

console = Console()
api_key = SecretManagerHelper.get_credential("root-station-198710", "data-cli-configs")[
    "DATAMESH_MANAGER_API_KEY"
]
os.environ["DATAMESH_MANAGER_API_KEY"] = api_key
folder_path = os.path.dirname(os.path.abspath(__file__))


def remove_types(schema: str):
    if isinstance(schema, dict):
        if "type" in schema:
            del schema["type"]
        for key in schema:
            remove_types(schema[key])
    elif isinstance(schema, list):
        for item in schema:
            remove_types(item)


def _get_schema(
    projet: str,
    raw_dataset: str,
    raw_table_id: str,
    data_column: str,
    date_column: str,
    periode: str,
):
    cloud_run_url = "https://dc-schema-generator-xgjjt7bsya-ew.a.run.app/fetch_schema"
    query_params = {
        "projet": projet,
        "dataset": raw_dataset,
        "table_id": raw_table_id,
        "data_column": data_column,
        "date_column": date_column,
        "periode": periode,
    }
    auth_token = (
        subprocess.check_output(["gcloud", "auth", "print-identity-token"])
        .decode()
        .strip()
    )
    headers = {"Authorization": f"Bearer {auth_token}"}

    try:
        response = requests.get(cloud_run_url, headers=headers, params=query_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"Erreur HTTP : {err}")
    except Exception as err:
        print(f"Autre erreur : {err}")


def generate_datacontract(
    projet_id: str,
    dataset_id: str,
    table_id: str,
    data_column: str,
    date_column: str,
    periode: str,
):
    datacontract_path = os.path.join(folder_path, f"../../output/dc_{table_id}.yaml")

    jsonschema = _get_schema(
        projet_id, dataset_id, table_id, data_column, date_column, periode
    )
    remove_types(jsonschema)
    with open("/tmp/dataschema.json", "w") as f:
        json.dump(jsonschema, f, indent=4)
    datacontract = yaml.safe_load(
        DataContract()
        .import_from_source(
            "jsonschema",
            "/tmp/dataschema.json",
        )
        .to_yaml()
    )
    (
        datacontract["info"]["owner"],
        datacontract["info"]["title"],
        datacontract["id"],
    ) = (
        "data-team",
        table_id,
        table_id,
    )
    with open(datacontract_path, "w") as f:
        yaml.dump(datacontract, f)
    return datacontract


def _get_contract_by_id(id: str):
    cloud_run_url = f"https://api.datamesh-manager.com/api/datacontracts/{id}"
    headers = {"x-api-key": os.getenv("DATAMESH_MANAGER_API_KEY")}
    try:
        response = requests.get(cloud_run_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        return None


def diff_datacontract(datacontract_id: str):
    datacontract_path = os.path.join(
        folder_path, f"../../output/dc_{datacontract_id}.yaml"
    )
    contract_by_id = _get_contract_by_id(datacontract_id)

    if not contract_by_id:
        console.print(f"New contract to deploy", style="green")
        return 1

    with open(f"/tmp/dc_{datacontract_id}.yaml", "w") as f:
        json.dump(_get_contract_by_id(datacontract_id), f, indent=4)

    result = DataContract(
        data_contract_file=f"/tmp/dc_{datacontract_id}.yaml", inline_definitions=True
    ).changelog(
        DataContract(data_contract_file=datacontract_path, inline_definitions=True)
    )
    console.print(result.changelog_str())
    return result.breaking_changes


def publish_datacontract(datacontract_id: str):
    datacontract_path = os.path.join(
        folder_path, f"../../output/dc_{datacontract_id}.yaml"
    )
    list = diff_datacontract(datacontract_id)
    if list:
        publish(datacontract_path)
    else:
        console.print(f"No change is detected", style="green")
