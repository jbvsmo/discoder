# coding: utf-8
""" Copyright (c) 2013 João Bernardo Vianna Oliveira

    This file is part of Discoder.

    Discoder is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Discoder is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Discoder.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

py_version = sys.version_info[:2]

install_requires = [
    'numpy >= 1.7',
]

if py_version < (3, 0):
    install_requires += [
        'python-daemon',
    ]

if py_version < (3, 2):
    install_requires += [
        'futures',
    ]

setup(
    name='discoder',
    version='0.5',
    packages=['discoder', 'discoder.lib', 'discoder.conv', 'discoder.distributed', 'discoder.proc'],
    url='http://146.164.98.15/redmine/projects/brstreams-discoder',
    license='',
    author='Joao Bernardo Oliveira',
    author_email='jbvsmo@gmail.com',
    description='Distributed Transcoding System',
    install_requires = install_requires,
)

