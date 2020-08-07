"""Set up mystrom2mqtt gateway."""
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.rst"), encoding="utf-8") as readme:
    long_description = readme.read()


setup(
    name="mystrom2mqtt",
    version="0.1.0",
    description="Transfer HTTP requests from myStrom devices to MQTT",
    long_description=long_description,
    url="https://github.com/home-assistant-ecosystem/mystrom2mqtt",
    author="Fabian Affolter",
    author_email="fabian@affolter-engineering.ch",
    license="ASL 2.0",
    install_requires=["python-multipart", "fastapi", "uvicorn", "toml", "netaddr", "asyncio_mqtt"],
    packages=find_packages(),
    zip_safe=True,
    include_package_data=True,
    entry_points={"console_scripts": [" mystrom2mqtt=mystrom2mqtt.__init__:run"]},
    keywords="iot mystrom mqtt homeassistant",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
)
