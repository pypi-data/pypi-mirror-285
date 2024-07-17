from setuptools import setup

setup(
    name='thedns',
    version='2.0.4',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://devnull.cn',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Identify your device with $system_id.[private,public].theca.cn',
    install_requires=[
        "requests",
        "theid"
    ]
)
