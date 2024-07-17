from setuptools import setup, find_packages

setup(
name="qpsychometric",
version="1.0.5",
description="A Python package containing implemented psychometrics for LLMs.",
packages=find_packages(),
project_urls={
        "Academic Article": "https://openreview.net/pdf/026597881acf1899856edfa5147390a6a60bd3a8.pdf",
    },
classifiers=[
"Programming Language :: Python :: 3",
"License :: OSI Approved :: Apache Software License",
"Operating System :: OS Independent",
],
include_package_data=True,
python_requires=">=3.8",
)