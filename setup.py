import os
from setuptools import setup, find_packages

setup(
    name="FastCoinExchange",
    version=__import__('fastcoinexchange-python').__version__,
    description=open(os.path.join(os.path.dirname(__file__), "DESCRIPTION")).read(),
    license="The MIT License (MIT)",
    keywords="coin, exchange",

    author="Alexander Yudkin",
    author_email="alexander@yudkin.com.ua",

    maintainer="Alexander Yudkin",
    maintainer_email="alexander@yudkin.com.ua",

    url="https://fastcoinexchange.com/",
    # packages=find_packages(exclude=["tests.*", "tests"]),
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)