# -*- coding: UTF-8 -*-
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='FlaskSQL',
    version='1.0.0',
    url='https://github.com/jzhong00/FlaskSQL/',
    license='MIT',
    author='Jason Zhong',
    author_email='jasonyzhong06@gmail.com',
    description='MySQL integration for Flask',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Set to markdown
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'PyMySQL'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
