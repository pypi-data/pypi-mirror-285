from setuptools import setup, find_namespace_packages
from gawsoft.api_client.version import __version__

with open('README.md','r') as r:
    long_description = r.read()

setup(
    name='gawsoft_api_client',
    version=__version__,
    packages=find_namespace_packages(include=['gawsoft.*']),
    namespace_packages=['gawsoft'],
    author="Gawsoft.pl",
    author_email="biuro@gawsoft.pl",
    description="Rest Api Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gawsoftpl/rest-api-client-framework-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Source Code": "https://github.com/gawsoftpl/rest-api-client-framework-python",
    },
    licence="MIT",
    python_requires='>=3.8',
)