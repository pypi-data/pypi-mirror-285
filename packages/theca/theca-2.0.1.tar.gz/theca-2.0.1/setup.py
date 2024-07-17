from setuptools import setup

setup(
    name='theca',
    version='2.0.1',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://github.com/xizhendu/theca-sdk-python',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Simple Python client library for TheCA.cn',
    # packages=['thedns'],
    install_requires=[
        "requests",
        "theid"
    ]
)
