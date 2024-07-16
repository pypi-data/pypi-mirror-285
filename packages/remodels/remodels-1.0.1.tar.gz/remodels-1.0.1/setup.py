# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['remodels',
 'remodels.data',
 'remodels.pipelines',
 'remodels.pointsModels',
 'remodels.qra',
 'remodels.qra.tester',
 'remodels.transformers',
 'remodels.transformers.VSTransformers']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.7.0,<3.8.0',
 'pandas<=1.5.3',
 'scikit-learn>=1.3.1,<2.0.0',
 'tqdm>=4.66.1,<5.0.0']

entry_points = \
{'console_scripts': ['remodels = remodels.__main__:main']}

setup_kwargs = {
    'name': 'remodels',
    'version': '1.0.1',
    'description': 'remodels',
    'long_description': "# remodels\n\n[![PyPI](https://img.shields.io/pypi/v/remodels.svg)][pypi_]\n[![Status](https://img.shields.io/pypi/status/remodels.svg)][status]\n[![Python Version](https://img.shields.io/pypi/pyversions/remodels)][python version]\n[![License](https://img.shields.io/pypi/l/remodels)][license]\n\n[![Documentation Status](https://readthedocs.org/projects/remodels/badge/?version=latest)][read the docs]\n[![Tests](https://github.com/zakrzewow/remodels/workflows/Tests/badge.svg)][tests]\n[![Codecov](https://codecov.io/gh/zakrzewow/remodels/branch/main/graph/badge.svg)][codecov]\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n[pypi_]: https://pypi.org/project/remodels/\n[status]: https://pypi.org/project/remodels/\n[python version]: https://pypi.org/project/remodels\n[read the docs]: https://remodels.readthedocs.io/en/latest/\n[tests]: https://github.com/zakrzewow/remodels/actions?workflow=Tests\n[codecov]: https://app.codecov.io/gh/zakrzewow/remodels\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n\nReModels is a Python package for probabilistic energy price forecasting using Quantile Regression Averaging (QRA) methods.\n\n## Installation\n\nYou can install _remodels_ via [pip] from [PyPI]:\n\n```console\n$ pip install remodels\n```\n\nAlternatively, you can install from source:\n\n```console\n$ git clone https://github.com/zakrzewow/remodels.git\n$ cd remodels\n$ pip install .\n```\n\n## Features\n\n- **Dataset Download**: access commonly used public datasets for transparent data acquisition.\n- **Data Preprocessing**: apply variance stabilizing transformation for improved data quality.\n- **Forecast Generation**: produce point and probabilistic forecasts with reference implementations of QRA variants.\n- **Result Evaluation**: compare predictions using dedicated metrics for fair and consistent evaluation.\n\nReModels provides a robust framework for researchers to compare different QRA methods and other forecasting techniques. It supports the development of new forecasting methods, extending beyond energy price forecasting.\n\nReModels simplifies and enhances energy price forecasting research with comprehensive tools and transparent methodologies.\n\nThe main functionality of the ReModels package are Variance Stabilizing Transformations and Quantile Regression Averaging variants.\n\nImplemented VSTs:\n\n- clipping,\n- clipping with the logarithm function\n- logistic transform\n- inverse hyperbolic sine transform\n- BoxCox transform\n- polynomial transform\n- mirror-log transformation\n- probability integral transform\n\nImplemented QRA variants:\n\n- QRA\n- QRM\n- FQRA\n- FQRM\n- sFQRA\n- sFQRM\n- LQRA\n- SQRA\n- SQRM\n\n## Usage\n\nVST basic usage example:\n\n```py\nimport numpy as np\nfrom remodels.transformers.VSTransformers import ArcsinhScaler, BoxCoxScaler, ClippingScaler, LogClippingScaler, LogisticScaler, MLogScaler, PITScaler, PolyScaler\n\nX = np.random.normal(0, 1, size=(100, 10))\nArcsinhScaler().fit_transform(X)\n```\n\nQRA basic usage example:\n\n```py\nimport numpy as np\nfrom remodels.qra import QRA, QRM, FQRA, FQRM, sFQRA, sFQRM, LQRA, SQRA, SQRM\n\nX = np.random.normal(0, 1, size=(100, 10))\ny = X.sum(axis=1)\n\nqra = QRA(quantile=0.5, fit_intercept=True)\nqra.fit(X, y).predict(X)\n```\n\nFor more advanced examples of high-level functionalities, please see the [Usage] or [Reference].\n\n## License\n\nDistributed under the terms of the [MIT license][license],\n_remodels_ is free and open source software.\n\n## Credits\n\nThis project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/project/remodels/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://github.com/zakrzewow/remodels/blob/main/LICENSE\n[usage]: https://remodels.readthedocs.io/en/latest/usage.html\n[reference]: https://remodels.readthedocs.io/en/latest/reference.html\n",
    'author': 'Grzegorz Zakrzewski',
    'author_email': 'zakrzew12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zakrzewow/remodels',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
