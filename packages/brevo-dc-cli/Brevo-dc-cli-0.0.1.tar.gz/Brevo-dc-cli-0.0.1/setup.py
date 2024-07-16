from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="Brevo-dc-cli",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    description="datacontract CLI for Brevo's data team",
    url="",
    author="Filah Anas",
    author_email="anas.filah@brevo.com",
    entry_points={
        "console_scripts": [
            "dc-cli = core.cli:cli",
        ],
    },
)
