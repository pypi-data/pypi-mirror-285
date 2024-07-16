from setuptools import setup, find_packages

setup(
    name='ithcoding',
    version='0.1',
    description='Python functions for controlling Arduino devices',
    author='hantaein',
    author_email='hti7220@naver.com',
    packages=find_packages(),
    install_requires=['pyserial'],
)
