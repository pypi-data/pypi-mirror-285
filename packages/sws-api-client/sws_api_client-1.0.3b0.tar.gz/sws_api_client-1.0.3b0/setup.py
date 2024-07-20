import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "1.0.3-beta"

# Setting up
setup(
    name="sws_api_client",
    version=VERSION,
    author="Mansillo, Daniele (CSI)",
    author_email="<daniele.mansillo@fao.com>",
    description="A Python client to easily interact with the FAO SWS REST APIs",
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["requests>=2.31.0", "pydantic>=2.7.4", "python-dotenv>=0.19.0"],
    keywords=["python", "fao", "sws", "rest", "api", "client"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    include_package_data=True,
    url="https://bitbucket.org/cioapps/sws-it-python-api-client/src/main/",
)
