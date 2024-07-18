from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='InstaToolkit',
    version='0.1.2',
    author='Himasha Herath',
    author_email='himasha626@gmail.com',
    description='A versatile toolkit for automating Instagram interactions',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/HimashaHerath/InstaToolkit',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Build Tools',
    ],
)