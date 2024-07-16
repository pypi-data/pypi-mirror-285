# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flspp']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.26.4,<2.0.0', 'scikit-learn>=1.4.2,<2.0.0']

setup_kwargs = {
    'name': 'flspp',
    'version': '0.1.5',
    'description': 'Implementation of the FLS++ algorithm for K-Means clustering.',
    'long_description': '[![Build Status](https://github.com/algo-hhu/FLSpp/actions/workflows/mypy-flake-test.yml/badge.svg)](https://github.com/algo-hhu/FLSpp/actions)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Supported Python version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)\n[![Stable Version](https://img.shields.io/pypi/v/flspp?label=stable)](https://pypi.org/project/flspp/)\n\n# FLS++\n\nAn implementation of the FLS++ algorithm for k-means Clustering, as presented in [1]. This is an improvement of the LS++ algorithm presented by Lattanzi and Sohler in [2].\n\nOne can think of the algorithm as working in 3 phases:\n\n1. Initializing centers with k-means++ (as presented in [3]).\n2. Improving the center set by performing local search swaps (for details, see [1]).\n3. Converging the solution with LLoyd\'s algorithm (also known as "the" k-means algorithm).\n\nIn [2] it is shown that `O(k log log k)` local search iterations yield a constant factor approximation. However, in both [1] and [2] it is shown that, in practice, a very small number of iterations (e.g. 20) already yields very good results, at very reasonable runtime.\n\nThe interface is built in the same way as scikit-learn\'s KMeans for better compatibility.\n\nIn the following plots, we compare the performance of FLS++ (GFLS++) with various local search steps (5, 10, 15) with k-means++ (kM++), greedy k-means++ (GkM++) and the local search algorithm [2] with 25 local search steps (GLS++). The results are computed for the [KDD Phy Test](https://www.kdd.org/kdd-cup/view/kdd-cup-2004/data) and the [Tower](https://www.worldscientific.com/doi/abs/10.1142/S0218195908002787) datasets and averaged over 50 runs.\n\n\n<p align="center">\n  <img src="https://raw.githubusercontent.com/algo-hhu/FLSpp/main/images/boxplots.png" alt="Boxplot Comparison for FLS++"/>\n</p>\n\n## References\n\n[1] Theo Conrads, Lukas Drexler, Joshua Könen, Daniel R. Schmidt and Melanie Schmidt. "Local Search k-means++ with Foresight" (2024)\n\n[2] Silvio Lattanzi and Christian Sohler. A better k-means++ algorithm via local search. In Proc.444\nof the 36th ICML, volume 97 of Proceedings of Machine Learning Research, pages 3662–3671.445\nPMLR, 09–15 Jun 2019\n\n[3] David Arthur and Sergei Vassilvitskii. K-means++: The advantages of careful seeding. In409\nProceedings of the 18th SODA, page 1027–1035, USA, 2007\n\n## Installation\n\n```bash\npip install flspp\n```\n\n## Example\n\n```python\nfrom flspp import FLSpp\n\nexample_data = [\n    [1.0, 1.0, 1.0],\n    [1.1, 1.1, 1.1],\n    [1.2, 1.2, 1.2],\n    [2.0, 2.0, 2.0],\n    [2.1, 2.1, 2.1],\n    [2.2, 2.2, 2.2],\n]\n\nflspp = FLSpp(n_clusters=2)\nlabels = flspp.fit_predict(example_data)\ncenters = flspp.cluster_centers_\n\nprint(labels) # [1, 1, 1, 0, 0, 0]\nprint(centers) # [[2.1, 2.1, 2.1], [1.1, 1.1, 1.1]]\n```\n\n## Development\n\nInstall [poetry](https://python-poetry.org/docs/#installation)\n```bash\ncurl -sSL https://install.python-poetry.org | python3 -\n```\n\nInstall clang\n```bash\nsudo apt-get install clang\n```\n\nSet clang variables\n```bash\nexport CXX=/usr/bin/clang++\nexport CC=/usr/bin/clang\n```\n\nInstall the package\n```bash\npoetry install\n```\n\nIf the installation does not work and you do not see the C++ output, you can build the package to see the stack trace\n```bash\npoetry build\n```\n\nRun the tests\n```bash\npoetry run python -m unittest discover tests -v\n```\n\n## Citation\n\nIf you use this code, please cite [the following paper](https://arxiv.org/abs/2406.02739v1):\n\n```\nTheo Conrads, Lukas Drexler, Joshua Könen, Daniel R. Schmidt and Melanie Schmidt. "Local Search k-means++ with Foresight" (2024). Accepted at SEA 2024.\n```\n',
    'author': 'Lukas Drexler',
    'author_email': 'lukas.drexler@hhu.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}
from build_extension import *
build(setup_kwargs)

setup(**setup_kwargs)
