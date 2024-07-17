# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pref_voting', 'pref_voting.io', 'pref_voting.tests']

package_data = \
{'': ['*'],
 'pref_voting': ['data/examples/condorcet_winner/*',
                 'data/voting_methods_properties.json',
                 'data/voting_methods_properties.json',
                 'data/voting_methods_properties.json.lock',
                 'data/voting_methods_properties.json.lock']}

install_requires = \
['filelock>=3.12.2,<4.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'nashpy>=0.0.40,<0.0.41',
 'networkx>=3.0,<4.0',
 'numba>=0.58.0,<0.59.0',
 'ortools>=9.8.0,<10.0.0',
 'prefsampling>=0.1.16,<0.2.0',
 'random2>=1.0.1,<2.0.0',
 'scipy>=1.0.0,<2.0.0',
 'tabulate>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'pref-voting',
    'version': '1.13.21',
    'description': 'pref_voting is a Python package that contains tools to reason about elections and margin graphs, and implementations of voting methods.',
    'long_description': 'pref_voting\n==========\n\n## Installation\n\nWith pip package manager:\n\n```bash\npip install pref_voting\n```\n\n## Documentation\n\nOnline documentation is available at [https://pref-voting.readthedocs.io](https://pref-voting.readthedocs.io).\n\n## Example Usage\n\nA profile (of linear orders over the candidates) is created by initializing a `Profile` class object.  Simply provide a list of rankings (each ranking is a tuple of numbers) and a list giving the number of voters with each ranking:\n\n```python\nfrom pref_voting.profiles import Profile\n\nrankings = [\n    (0, 1, 2, 3), \n    (2, 3, 1, 0), \n    (3, 1, 2, 0), \n    (1, 2, 0, 3), \n    (1, 3, 2, 0)]\n\nrcounts = [5, 3, 2, 4, 3]\n\nprof = Profile(rankings, rcounts=rcounts)\n```\n\nThe function `generate_profile` is used to generate a profile for a given number of candidates and voters:  \n\n```python\nfrom pref_voting.generate_profiles import generate_profile\n\n# generate a profile using the Impartial Culture probability model\nprof = generate_profile(3, 4) # prof is a Profile object\n\n# generate a profile using the Impartial Anonymous Culture probability model\nprof = generate_profile(3, 4, probmod = "IAC") # prof is a Profile object \n```\n\nTo use one of the many voting methods, import the function from `pref_voting.voting_methods` and apply it to the profile: \n\n```python\nfrom pref_voting.generate_profiles import generate_profile\nfrom pref_voting.voting_methods import *\n\nprof = generate_profile(3, 4)\nsplit_cycle(prof) # returns the sorted list of winning candidates\nsplit_cycle.display(prof) # display the winning candidates\n\n```\n\n## Questions?\n\nFeel free to [send an email](https://pacuit.org/) if you have questions about the project.\n\n## License\n\n[MIT](https://github.com/jontingvold/pyrankvote/blob/master/LICENSE.txt)\n',
    'author': 'Eric Pacuit',
    'author_email': 'epacuit@umd.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/voting-tools/pref_voting',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
