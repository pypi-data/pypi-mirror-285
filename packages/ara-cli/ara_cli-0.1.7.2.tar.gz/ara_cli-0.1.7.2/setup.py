from setuptools import setup, find_packages
import os

# Import version number
version = {}
with open("./ara_cli/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="ara_cli",
    version=version['__version__'],
    packages=find_packages(),
    include_package_data=True,  # Add this line
    entry_points={
        "console_scripts": [
            "ara = ara_cli.__main__:cli",
            "ara-list = ara_cli.__main__:list",
        ],
    },
    install_requires=[
        'langchain',
        'langchain-community',
        'langchain_openai',
        'llama-index',
        'llama-index-llms-openai',
        'llama-index-retrievers-bm25',
        'openai',
        'markdown-it-py',
        'json-repair',
        # Add your package dependencies here
    ],
)

