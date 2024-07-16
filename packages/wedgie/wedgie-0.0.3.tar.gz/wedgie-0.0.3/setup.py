from setuptools import setup, find_packages

VERSION = '0.0.3'

setup(
    name="wedgie",
    version=VERSION,
    author="Chad Roberts",
    author_email="jcbroberts@gmail.com",
    description="A public Python package for miscellaneous reusable functionality",
    long_description="A public Python package for miscellaneous reusable functionality",
    packages=find_packages(),
    install_requires=[
        "structlog",
        "tinydb >= 4.8.0",
        "tabulate >= 0.9.0",
    ],
    keywords=["python"],

    # url="https://github.com/...",
    # project_urls={
    #     "Bug Tracker": "https://github.com/...",
    # },

    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3.10",
        "Natural Language :: English",
    ]
)
