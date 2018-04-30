# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

setup(
    name="FastCoinExchange",
    version=__import__('fastex').__version__,
    description=open(os.path.join(os.path.dirname(__file__), "DESCRIPTION")).read(),
    license="The MIT License (MIT)",
    keywords="coin, exchange",

    author="Alexander Yudkin",
    author_email="san4ezy@gmail.com",

    maintainer="Alexander Yudkin",
    maintainer_email="san4ezy@gmail.com",

    url="https://github.com/fastcoinexchange/fastcoinexchange-python",
    packages=find_packages(exclude=[]),
    install_requires=[
        "cryptography==1.9",
        "idna==2.5",
        "pycrypto==2.6.1",
        "pyOpenSSL==17.1.0",
        "requests==2.18.1",
        "simplejson==3.11.1",
        "six>=1.10.0",
        "urllib3==1.21.1",
        "virtualenv==15.1.0",
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
