from setuptools import setup, find_packages

with open("README.md","r") as f:
    description = f.read()

setup(
    name='marketplace_hub_api',
    version='0.1',
    description = 'Find, Connect and Manage APIs',
    author = 'marketplace-hub-api',
    author_email = 'hello@zylalabs.com',
    url = 'https://github.com/Zyla-Labs/pypi-api-hub',
    keywords = ['Api Hub', 'APIs', 'Find, Connect and Manage APIs', 'APIs Management', 'APIs Connection', 'APIs Integration', 'APIs Automation', 'APIs Development'],
    packages=find_packages(),
    install_requires=[
        
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)