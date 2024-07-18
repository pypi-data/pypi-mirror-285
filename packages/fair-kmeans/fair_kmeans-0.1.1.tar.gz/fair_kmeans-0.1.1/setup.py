# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fair_kmeans']

package_data = \
{'': ['*'], 'fair_kmeans': ['lemon/*', 'lemon/bits/*', 'lemon/concepts/*']}

install_requires = \
['numpy>=1.26.4,<2.0.0', 'scikit-learn>=1.4.2,<2.0.0']

setup_kwargs = {
    'name': 'fair-kmeans',
    'version': '0.1.1',
    'description': 'Fair K-Means produces a fair clustering assignment according to the fairness definition of Chierichetti et al. Each point has a binary color, and the goal is to assign the points to clusters such that the number of points with different colors in each cluster is the same and the cost of the clusters is minimized.',
    'long_description': '[![Build Status](https://github.com/algo-hhu/fair-kmeans/actions/workflows/mypy-flake-test.yml/badge.svg)](https://github.com/algo-hhu/fair-kmeans/actions)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Supported Python version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)\n[![Stable Version](https://img.shields.io/pypi/v/fair-kmeans?label=stable)](https://pypi.org/project/fair-kmeans/)\n\n# Fair K-Means\n\nFair K-Means produces a fair clustering assignment according to the fairness definition of Chierichetti et al. [1]. Each point has a binary color assigned to it. The goal is to assign the points to clusters such that the number of points with different colors in each cluster is the same. The algorithm also works with weights, so each point can participate with a different weight in the coloring.\n\nThe algorithm works as follows, assuming that the binary colors are red and blue:\n1. A matching between the red and blue points is computed such that the cost (the point distances) of the matching is minimized.\n2. The mean of each matched pair is computed.\n3. A K-Means++ clustering of all the means is computed, and the point pairs are assigned to the clusters of their means.\n\nThe matching between the red and blue points is computed using the [Lemon C++ Library](https://lemon.cs.elte.hu/trac/lemon). The library is included in the package and does not need to be installed separately. Only the needed files were included, and a complete version of the library can be found [here](https://lemon.cs.elte.hu/trac/lemon). A copyright notice is included [here](fair_kmeans/lemon/LICENSE).\n\n### References\n\n[1] Flavio Chierichetti, Ravi Kumar, Silvio Lattanzi, and Sergei Vassilvitskii, Fair clustering through fairlets, Proceedings of the 30th Annual Conference on Neural Information Processing Systems (NIPS), 2017, pp. 5036–5044.\n\n## Installation\n\n```bash\npip install fair-kmeans\n```\n\n## Example\n\n```python\nfrom fair_kmeans import FairKMeans\n\nexample_data = [\n    [1.0, 1.0, 1.0],\n    [1.1, 1.1, 1.1],\n    [1.2, 1.2, 1.2],\n    [2.0, 2.0, 2.0],\n    [2.1, 2.1, 2.1],\n    [2.2, 2.2, 2.2],\n]\n\nexample_colors = [1, 1, 1, 0, 0, 0]\n\nkm = FairKMeans(n_clusters=2, random_state=0)\nkm.fit(example_data, color=example_colors)\nlabels = km.labels_\ncenters = km.cluster_centers_\n\nprint(labels) # [1, 0, 0, 1, 0, 0]\nprint(centers) # [[1.65, 1.65, 1.65], [1.5, 1.5, 1.5]]\n```\n\n## Example with Weights\n\n```python\nfrom fair_kmeans import FairKMeans\n\nexample_data = [\n    [1.0, 1.0, 1.0],\n    [1.1, 1.1, 1.1],\n    [1.2, 1.2, 1.2],\n    [2.0, 2.0, 2.0],\n    [2.1, 2.1, 2.1],\n    [2.2, 2.2, 2.2],\n]\n\nexample_colors = [1, 1, 1, 0, 0, 0]\nexample_weights = [2, 2, 1, 1, 1, 3]\n\nkm = FairKMeans(n_clusters=2, random_state=0)\nkm.fit(example_data, color=example_colors, sample_weight=example_weights)\nlabels = km.labels_\ncenters = km.cluster_centers_\n\nprint(labels) # [1, 1, 0, 1, 1, 0]\nprint(centers) # [[0.85, 0.85, 0.85], [1.28, 1.28, 1.28]]\n```\n\n## Development\n\nInstall [poetry](https://python-poetry.org/docs/#installation)\n```bash\ncurl -sSL https://install.python-poetry.org | python3 -\n```\n\nInstall clang\n```bash\nsudo apt-get install clang\n```\n\nSet clang variables\n```bash\nexport CXX=/usr/bin/clang++\nexport CC=/usr/bin/clang\n```\n\nInstall the package\n```bash\npoetry install\n```\n\nIf the installation does not work and you do not see the C++ output, you can build the package to see the stack trace\n```bash\npoetry build\n```\n\nRun the tests\n```bash\npoetry run python -m unittest discover tests -v\n```\n\n## Citation\n\nIf you use this code, please cite [the following paper](https://arxiv.org/abs/2406.02739v1):\n\n```\nMelanie Schmidt, Chris Schwiegelshohn and Christian Sohler.\n"Fair Coresets and Streaming Algorithms for Fair k-Means Clustering" (2020).\nApproximation and Online Algorithms. WAOA 2019.\nLecture Notes in Computer Science, vol 11926. Springer.\n```\n',
    'author': 'Melanie Schmidt',
    'author_email': 'mschmidt@hhu.de',
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
