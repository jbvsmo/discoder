import sys
try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

install_requires = [
    'numpy >= 1.7',
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

