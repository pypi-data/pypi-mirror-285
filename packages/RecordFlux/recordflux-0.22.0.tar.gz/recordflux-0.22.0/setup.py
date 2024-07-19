# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rflx',
 'rflx.converter',
 'rflx.generator',
 'rflx.ide.gnatstudio',
 'rflx.lang',
 'rflx.ls',
 'rflx.model',
 'rflx.pyrflx',
 'rflx.specification']

package_data = \
{'': ['*'],
 'rflx': ['ide/vscode/recordflux.vsix', 'rapidflux/*', 'templates/*']}

install_requires = \
['attrs>=22.1,<24',
 'defusedxml>=0.7,<0.8',
 'importlib_resources>=6,<7',
 'pydantic>=2,<3',
 'pydotplus>=2,<3',
 'pygls>=1.1,<2',
 'ruamel.yaml>=0.18,<0.19',
 'z3-solver>=4,<4.12.3']

entry_points = \
{'console_scripts': ['rflx = rflx.cli:run']}

setup_kwargs = {
    'name': 'RecordFlux',
    'version': '0.22.0',
    'description': 'A toolset for the formal specification and generation of verifiable binary parsers, message generators and protocol state machines.',
    'long_description': "# [RecordFlux](https://github.com/AdaCore/RecordFlux/)\n\n[![PyPI](https://img.shields.io/pypi/v/RecordFlux?color=blue)](https://pypi.org/project/RecordFlux/)\n[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/5052/badge)](https://bestpractices.coreinfrastructure.org/projects/5052)\n\nRecordFlux is a toolset for the formal specification and generation of verifiable binary parsers, message generators and protocol state machines.\n\nSee the [website](https://www.adacore.com/recordflux), the [user's guide](https://docs.adacore.com/live/wave/recordflux/html/recordflux_ug/index.html) and the [language reference](https://docs.adacore.com/live/wave/recordflux/html/recordflux_lr/index.html) for more information.\n\n## Contribution and Feedback\n\nContributions and feedback to RecordFlux are very welcome. To discuss a bug or an enhancement, [open a ticket on GitHub](https://github.com/AdaCore/RecordFlux/issues/new/choose) and select the appropriate issue template. Please give sufficient information about your issue, the software version you are using and your environment such that the developers can understand and (if necessary) reproduce the problem. If none of the provided issue templates fit your needs, feel free to open [a blank issue](https://github.com/AdaCore/RecordFlux/issues/new).\n\nSee the [development guide](https://github.com/AdaCore/RecordFlux/blob/main/doc/development_guide/index.rst) on how to contribute to RecordFlux.\n\n## Licence\n\nThis software is licensed under the `Apache-2.0`. See the `LICENSE` file for the full license text.\n",
    'author': 'Tobias Reiher',
    'author_email': 'reiher@adacore.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.adacore.com/recordflux',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.12',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
