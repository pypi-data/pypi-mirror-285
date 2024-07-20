from setuptools import setup, find_packages

setup(
    name='cjggg060615',
    version='0.1',
    description='Python functions for controlling Arduino devices',
    author='wowogud',
    author_email='jhc06150615@gmail.com',
    packages=find_packages(),
    install_requires=['pyserial'],
)