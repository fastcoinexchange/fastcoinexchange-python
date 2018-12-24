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

    maintainer="Olexandr Shalakhin",
    maintainer_email="olexandr@shalakhin.com",

    url="https://github.com/fastcoinexchange/fastcoinexchange-python",
    packages=find_packages(exclude=[]),
    install_requires=[
        "cryptography==2.4.2",
        "idna==2.8",
        "pycrypto>=2.6.1",
        "pyOpenSSL>=18.0.0",
        "requests>=2.21.0",
        "simplejson>=3.16.0",
        "six>=1.12.0",
        "urllib3>=1.24.1",
        "virtualenv>=16.1.0",
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
