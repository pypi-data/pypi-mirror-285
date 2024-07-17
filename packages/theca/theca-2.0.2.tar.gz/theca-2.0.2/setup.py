from setuptools import setup

setup(
    name='theca',
    version='2.0.2',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://devnull.cn',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Python library to run your own private CA.',
    # packages=['thedns'],
    install_requires=[
        "requests",
        "theid"
    ]
)
