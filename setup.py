import os
from setuptools import setup, find_packages

setup(
    name="FastCoinExchange",
    version=__import__('fastex').__version__,
    description=open(os.path.join(os.path.dirname(__file__), "DESCRIPTION")).read(),
    license="The MIT License (MIT)",
    keywords="coin, exchange",

    author="Alexander Yudkin",
    author_email="alexander@yudkin.com.ua",

    maintainer="Alexander Yudkin",
    maintainer_email="alexander@yudkin.com.ua",

    url="https://fastcoinexchange.com/",
    packages=find_packages(exclude=[]),
    install_requires=[
        "booby==0.7.0",
        "certifi==2017.4.17",
        "chardet==3.0.4",
        "cryptography==1.9",
        "pyOpenSSL==17.1.0",
        "requests==2.18.1",
        "simplejson==3.11.1",
        "urllib3==1.21.1",
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
