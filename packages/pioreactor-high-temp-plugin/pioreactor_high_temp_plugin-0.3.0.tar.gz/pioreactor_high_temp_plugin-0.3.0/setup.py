# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="pioreactor-high-temp-plugin",
    version="0.3.0",
    license="MIT",
    description="Using this risks damaging your Pioreactor or harming yourself. Only use with the high-temp plastics provided.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="cam@pioreactor.com",
    author="Pioreactor",
    url="https://github.com/Pioreactor/pioreactor-high-temp-plugin",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "pioreactor.plugins": "pioreactor_high_temp_plugin = pioreactor_high_temp_plugin"
    },
)
