from setuptools import setup, find_packages

setup(
    name="bottles-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
        "anthropic",
    ],
    entry_points={
        "console_scripts": [
            "bottles=bottles.cli:cli",
        ],
    },
)
