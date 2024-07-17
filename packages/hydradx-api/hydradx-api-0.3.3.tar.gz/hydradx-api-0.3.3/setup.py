# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hydradxapi', 'hydradxapi.pallets']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.7,<9.0.0',
 'pytest>=7.4.2,<8.0.0',
 'substrate-interface>=1.7.4,<2.0.0']

setup_kwargs = {
    'name': 'hydradx-api',
    'version': '0.3.3',
    'description': 'HydraDX interface',
    'long_description': None,
    'author': 'Martin Hloska',
    'author_email': 'martin.hloska@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/enthusiastmartin/hydradx-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
