#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="backup_ssm",
    version="0.1",
    author="Michael De La Rue",
    author_email="michael-paddle@fake.github.com",
    description="Backup your AWS SSM parameters - part of backup-cloud",
    long_description=long_description,
    url="https://github.com/backup-cloud/backup-ssm",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": ["aws-ssm-backup = backup_cloud_ssm.aws_ssm_cli:main"]
    },
    install_requires=["boto3"],
)
