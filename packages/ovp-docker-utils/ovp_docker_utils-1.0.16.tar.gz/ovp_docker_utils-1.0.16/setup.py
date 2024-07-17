from setuptools import setup, find_packages

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent/'ovp_docker_utils'))
from __version__ import __version__


NAME = 'ovp_docker_utils'
VERSION = __version__
DESCRIPTION = 'O3R docker deployment utilities'
LONG_DESCRIPTION = 'A package for deployment and testing of code for the O3R camera system via docker container on the OVP8XX platform.'

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="ifm gmbh",
    author_email="support.efector.object.ident@ifm.com",
    packages=find_packages(include=['ovp_docker_utils']),
    install_requires=[
        'pyyaml',
        'scp',
        'ifm3dpy',
        'pydantic',
        'semver',
    ],
    entry_points={
        'console_scripts': [
            'ovp_docker_utils=ovp_docker_utils.ovp_docker_utils:app']
    },
    license='Apache 2.0',
)
