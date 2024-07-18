from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="brevo-dc-cli",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    description="datacontract CLI for Brevo's data team",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    author="Filah Anas",
    author_email="anas.filah@brevo.com",
    entry_points={
        "console_scripts": [
            "brevo-dc-cli = core.cli:cli",
        ],
    },
)
