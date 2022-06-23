#!/usr/bin/python


from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='sspam',
    description=' A symbolic simplifier using pattern matching',
    long_description=long_description,
    version='0.2.0',
    url='https://github.com/pypa/sampleproject',
    author='Ninon Eyrolles',
    author_email='neyrolles@quarkslab.com',
    license='BSD',
    classifiers=[
	'Development Status :: 4 - Beta',
	'Intended Audience :: Science/Research',
	'Topic :: Software Development :: Build Tools',
	'Topic :: Security',
	'Topic :: Scientific/Engineering',
	'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='simplification mixed expressions pattern-matching',
    packages=["sspam", "sspam.tools"],
    entry_points={
        'console_scripts': [
            'sspam = sspam.__main__:main'
        ]
    },
)
