# setup.py
from setuptools import setup, find_packages

setup(
    name='paravastu',
    version='1.6',
    author='Paravastu Lab',
    author_email='dmd9@gatech.edu',
    description='A utility package for handling files and paths, particularly with Dropbox integration.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'ipywidgets', 'numpy', 'ipython'
    ],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
