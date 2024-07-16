# dc-cli

`dc-cli` is a command-line interface (CLI) tool for managing data contracts in Brevo. This tool provides commands to generate, compare, publish, and perform all operations related to data contracts.

## Installation

To install `dc-cli`, use pip:

```bash
pip install dc-cli
```

## Usage
The dc-cli tool provides several commands for working with data contracts. Below is a list of the available commands and their descriptions.
### Generate Data Contract
```bash
dc-cli -m datacontract generate [gcp_table_id]
```
### Diff Data Contracts
Compare data contracts to identify differences.
```bash
dc-cli -m datacontract diff
```


### Publish Data Contract

```bash
dc-cli -m datacontract publish
```

### All Operations
```bash
dc-cli -m datacontract all [gcp_table_id]
```


## Command Options
-m: Specifies the module to use, in this case, datacontract.


## Build and deploy the pypi

pip install twine
python setup.py sdist bdist_wheel
<!-- twine upload dist/* -->
twine upload --repository-url https://upload.pypi.org/legacy/ --skip-existing --verbose dist/* --password <your_api_token>
