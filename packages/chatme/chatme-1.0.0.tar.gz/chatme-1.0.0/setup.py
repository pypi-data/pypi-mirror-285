from setuptools import setup, find_packages

setup(
    name='chatme',
    version='1.0.0',
    packages=find_packages(),
    python_requires='>=3.6',
    author='MrFidal',
    author_email='mrfidal@proton.me',
    description='A simple Python package for terminal-based chat applications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ByteBreach/chatme',
)
