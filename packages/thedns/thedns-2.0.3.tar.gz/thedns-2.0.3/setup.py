from setuptools import setup

setup(
    name='thedns',
    version='2.0.3',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://devnull.cn',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Python module to register your device as "_device_id_.{private,public}.theca.cn"',
    install_requires=[
        "requests",
        "theid"
    ]
)
