from setuptools import setup, find_packages

setup(
    name='kimtaewoncoding',
    version='0.1',
    description='Python functions for controlling Arduino devices',
    author='kimtaewoncoding',
    author_email='kimtw5967@gmail.com',
    packages=find_packages(),
    install_requires=['pyserial'],
)