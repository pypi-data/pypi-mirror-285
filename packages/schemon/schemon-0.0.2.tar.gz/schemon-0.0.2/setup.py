from setuptools import setup, find_packages

import os
import subprocess

VERSION = '0.0.2'

def create_git_tag(version):
    try:
        subprocess.check_call(['git', 'tag', f'v{version}'])
        subprocess.check_call(['git', 'push', 'origin', f'v{version}'])
    except subprocess.CalledProcessError as e:
        print(f"Error creating or pushing tag: {e}")

create_git_tag(VERSION)

setup(
    name='schemon',
    version=VERSION,
    packages=find_packages(),
    license='Apache-2.0',
    install_requires=[
        'future==1.0.0',
        'greenlet==3.0.3',
        'pure-sasl==0.6.2',
        'PyHive==0.7.0',
        'python-dateutil==2.9.0.post0',
        'PyYAML==6.0.1',
        'six==1.16.0',
        'SQLAlchemy==2.0.31',
        'thrift==0.20.0',
        'thrift-sasl==0.4.3',
        'typing_extensions==4.12.2',
        'python-dotenv==1.0.0',
        'databricks-sql-connector[sqlalchemy]==3.2.0',
        'prettytable==3.10.0',
        'mysql-connector-python==8.0.30'
    ],
    entry_points={
        'console_scripts': [
            'schemon=schemon.main:main', 
        ],
    },
)
