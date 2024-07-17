from setuptools import setup

setup(
    name='thedns',
    version='2.0.1',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://github.com/xizhendu/thedns-sdk-python',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Simple Python client library for TheDNS.cn',
    # packages=['thedns'],
    install_requires=[
        "requests",
        "theid"
    ]
)
