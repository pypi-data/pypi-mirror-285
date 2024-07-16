from setuptools import setup

setup(
    name='theid',
    version='1.0.3',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://github.com/xizhendu/theid-sdk-python',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Identity Service for https://devnull.cn',
    # packages=['thedns'],
    install_requires=[
        "requests",
    ]
)
