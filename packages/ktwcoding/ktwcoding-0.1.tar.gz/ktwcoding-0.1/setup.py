from setuptools import setup, find_packages

setup(
    name='ktwcoding',
    version='0.1',
    description='Python functions for controlling Arduino devices',
    author='taeu',
    author_email='rlaxodn0428@naver.com',
    packages=find_packages(),
    install_requires=['pyserial'],
)