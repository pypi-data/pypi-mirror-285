from setuptools import setup, find_packages
import codecs
import re
import os.path
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


setup(
    name='prefect-yeedu-operator',
    version='v1.0.8',
    description='Submission and monitoring of jobs and notebooks using the Yeedu API in prefect. ',
    long_description_content_type='text/markdown',
    author='Yeedu Admin',
    author_email='yeedu_devops@yeedu.io',
    packages=find_packages(),
   install_requires=[
    'requests>=2.27',
    'websocket-client>=1.8.0',
    'rel>=0.4.9.19',
    'prefect_github==0.2.6',
    'prefect>=2.16.9'
    ],
    license='All Rights Reserved',
)

