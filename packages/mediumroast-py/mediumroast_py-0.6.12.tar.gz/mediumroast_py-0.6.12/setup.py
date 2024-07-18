# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mediumroast_py', 'mediumroast_py.api']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=42.0.6,<43.0.0',
 'pygithub>=2.3.0,<3.0.0',
 'pyjwt>=2.8.0,<3.0.0',
 'python-dotenv>=1.0.1,<2.0.0',
 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['test = run_tests:main']}

setup_kwargs = {
    'name': 'mediumroast-py',
    'version': '0.6.12',
    'description': 'This Python package provides a Software Development Kit (SDK) for interacting with Mediumroast for GitHub. It is used internally by Mediumroast, Inc. and meant for developers to make use of.',
    'long_description': "# mediumroast_py\n\n## Introduction\n\nThis Python package provides a Software Development Kit (SDK) for interacting with Mediumroast for GitHub. It is used internally by Mediumroast, Inc. and meant for developers to make use of.\n\n### Notice\nThe SDK is in active development and is subject to change. The SDK is not yet stable and should not be used in production environments. \n\n## Installation\n\nTo install the package, you can use pip:\n\n```bash\npip install mediumroast_py\n```\n\n## Usage\nTo use the package, you will need to import the `mediumroast_py` modules and classes. The package provides three main classes for interacting with objects: `Companies`, `Interactions`, and `Users`.\n\n### Authentication\nTo use the package, you will need to authenticate with the Mediumroast API using the `GitHubAuth` class. Here is an example of how to authenticate with the Mediumroast API using a GitHub App installation and a private key file. You will need to set the `MR_CLIENT_ID`, `MR_APP_ID`, and `YOUR_INSTALLATION_ID` environment variables to the appropriate values for your GitHub App installation. You will also need to set the `YOUR_PEM_FILE` environment variable to the path of your private key file. Here is an example of how to authenticate with the Mediumroast API using a GitHub App installation and a private key file.\n\n```python\nfrom mediumroast_py.api import Companies, Interactions, Users\nfrom mediumroast_py.api.authorize import GitHubAuth\n\nauth = GitHubAuth(env={'clientId': os.getenv('MR_CLIENT_ID')})\ntoken = auth.get_access_token_pem(\n      os.getenv('YOUR_PEM_FILE'), \n      os.getenv('MR_APP_ID'), \n      os.getenv('YOUR_INSTALLATION_ID')\n)\n```\n\n### Companies\nThe `Companies` class provides methods for interacting with companies in Mediumroast. You can use the `get_all` method to get information about all companies.\n\n```python\ncompany_ctl = Companies(token_info['token'], os.getenv('YOUR_ORG') , process_name)\ncompanies = company_ctl.get_all()\n```\n\n### Interactions\nThe `Interactions` class provides methods for interacting with interactions in Mediumroast. You can use the `get_all` method to get information about all interactions.\n\n```python\ninteraction_ctl = Interactions(token_info['token'], os.getenv('YOUR_ORG') , process_name)\ninteractions = interaction_ctl.get_all()\n```\n\n## Issues\nIf you encounter any issues with the SDK, please report them on the [mediumroast_py issues](https://github.com/mediumroast/mediumroast_py/issues) page.\n",
    'author': 'Michael Hay',
    'author_email': 'michael.hay@mediumroast.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mediumroast/mediumroast_py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
