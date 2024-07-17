from setuptools import setup

setup(
    name='theid',
    version='1.0.7',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://devnull.cn',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Identity Service',
    # packages=['thedns'],
    install_requires=[
        "requests",
    ]
)
