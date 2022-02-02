from glob import glob
from setuptools import setup

setup (name = 'logsrv',
       version = '0.1',
       description = 'A simple logging server working over websockets',
       package_dir = {'logsrv': 'src'},
       packages = ['logsrv'],
       install_requires=['websockets'])
