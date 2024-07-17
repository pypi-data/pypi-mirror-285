
# Licensed under the MIT license.

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

setup(
    name = 'ModelCompresLight',
    version = '0.1.2',
    author = 'CO-AI Team',
    author_email = '710783765@qq.com',
    description = 'Lighter Model Ensemble',
    long_description = read('README.rst'),
    license = 'MIT',
    url = None,

	packages=find_packages('ModelCompresLight',exclude=["*.ModelZoo"]),
	package_dir = {'':'ModelCompresLight'},
    python_requires = '>=3.6.2',
    install_requires = [
        'thop',

    ]


)
