from setuptools import setup

setup(
    name='thepulse',
    version='1.0.7',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://github.com/xizhendu/thepulse-sdk-python',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Simple Python client library for https://devnull.cn/pulse',
    install_requires=[
        "requests",
    ]
)
