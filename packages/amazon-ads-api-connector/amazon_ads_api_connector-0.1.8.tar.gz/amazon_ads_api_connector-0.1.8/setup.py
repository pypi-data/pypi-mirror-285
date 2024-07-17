from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="amazon-ads-api-connector",
    version="0.1.8",
    packages=find_packages(),
    install_requires=[
        "httpx",
    ],
    author="Markus U. Wahl",
    long_description=description,
    long_description_content_type="text/markdown",
    description="API wrapper for the Amazon Ads API",
)
