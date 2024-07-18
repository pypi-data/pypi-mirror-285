from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tptest",
    version="0.1.0",
    author="Nopaque Limited",
    author_email="info@nopaque.co.uk",
    description="A CLI tool for running tests against IVRs using the TotalPath Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nopaque/tptest",
    packages=find_packages(),
    install_requires=[
        "click",
        "websockets",
        "asyncclick",
    ],
    entry_points={
        "console_scripts": [
            "tptest=tptest.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
