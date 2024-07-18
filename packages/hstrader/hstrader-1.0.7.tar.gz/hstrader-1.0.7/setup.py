# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hstrader',
 'hstrader.config',
 'hstrader.helpers',
 'hstrader.hstrader',
 'hstrader.models',
 'hstrader.services']

package_data = \
{'': ['*']}

install_requires = \
['pydantic', 'requests', 'websockets']

setup_kwargs = {
    'name': 'hstrader',
    'version': '1.0.7',
    'description': '',
    'long_description': '',
    'author': 'Hybrid Solutions',
    'author_email': 'dev@hybridsolutions.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
