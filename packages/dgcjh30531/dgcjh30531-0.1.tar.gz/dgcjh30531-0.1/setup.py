from setuptools import setup, find_packages

setup(
    name='dgcjh30531',
    version='0.1',
    description='Python functions for controlling Arduino devices',
    author='cjh30531',
    author_email='yw060817@gmail.com',
    packages=find_packages(),
    install_requires=['pyserial'],
)