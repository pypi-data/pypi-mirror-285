# brevo-dc-cli

`brevo-dc-cli` is a command-line interface (CLI) tool for managing data contracts in Brevo. This tool provides commands to generate, compare, publish, and perform all operations related to data contracts.

## Installation

To install `brevo-dc-cli`, use pip:

```bash
pip install brevo-dc-cli
```

## Usage
The dc-cli tool provides several commands for working with data contracts. Below is a list of the available commands and their descriptions.
### Generate Data Contract
```bash
brevo-dc-cli datacontract -m  generate [project_id] [dataset_id] [table_id] [data_column] [date_column]

```
### Diff Data Contracts
Compare data contracts to identify differences.
```bash
brevo-dc-cli datacontract -m diff [table_id]
```


### Publish Data Contract

```bash
brevo-dc-cli datacontract -m publish [gcp_table_id]
```

### All Operations
```bash
brevo-dc-cli datacontract -m all [project_id] [dataset_id] [table_id] [data_column] [date_column]
```

## Command Options
-m: Specifies the module to use, in this case, datacontract.


## Build and deploy the pypi

pip install twine
pip install wheel

python setup.py sdist bdist_wheel
twine upload --repository-url https://upload.pypi.org/legacy/ --skip-existing --verbose dist/* --password <your_api_token>
