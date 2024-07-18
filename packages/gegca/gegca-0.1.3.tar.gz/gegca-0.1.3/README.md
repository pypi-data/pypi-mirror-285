# Global Emissions Global Climate Assessment

<!---
Can use start-after and end-before directives in docs, see
https://myst-parser.readthedocs.io/en/latest/syntax/organising_content.html#inserting-other-documents-directly-into-the-current-document
-->

<!--- sec-begin-description -->

Global-mean climate assessment of global emissions scenarios.



[![CI](https://github.com/znicholls/gegca/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/znicholls/gegca/actions/workflows/ci.yaml)
[![Coverage](https://codecov.io/gh/znicholls/gegca/branch/main/graph/badge.svg)](https://codecov.io/gh/znicholls/gegca)
[![Docs](https://readthedocs.org/projects/gegca/badge/?version=latest)](https://gegca.readthedocs.io)

**PyPI :**
[![PyPI](https://img.shields.io/pypi/v/gegca.svg)](https://pypi.org/project/gegca/)
[![PyPI: Supported Python versions](https://img.shields.io/pypi/pyversions/gegca.svg)](https://pypi.org/project/gegca/)
[![PyPI install](https://github.com/znicholls/gegca/actions/workflows/install.yaml/badge.svg?branch=main)](https://github.com/znicholls/gegca/actions/workflows/install.yaml)

**Other info :**
[![Licence](https://img.shields.io/github/license/znicholls/gegca.svg)](https://github.com/znicholls/gegca/blob/main/LICENCE)
[![Last Commit](https://img.shields.io/github/last-commit/znicholls/gegca.svg)](https://github.com/znicholls/gegca/commits/main)
[![Contributors](https://img.shields.io/github/contributors/znicholls/gegca.svg)](https://github.com/znicholls/gegca/graphs/contributors)


<!--- sec-end-description -->

Full documentation can be found at:
[gegca.readthedocs.io](https://gegca.readthedocs.io/en/latest/).
We recommend reading the docs there because the internal documentation links
don't render correctly on GitHub's viewer.

## Installation

<!--- sec-begin-installation -->

Global Emissions Global Climate Assessment can be installed with pip, mamba or conda:

```bash
pip install gegca
mamba install -c conda-forge gegca
conda install -c conda-forge gegca
```

Additional dependencies can be installed using

```bash
# To add plotting dependencies
pip install gegca[plots]
# To add notebook dependencies
pip install gegca[notebooks]

# If you are installing with conda, we recommend
# installing the extras by hand because there is no stable
# solution yet (issue here: https://github.com/conda/conda/issues/7502)
```

<!--- sec-end-installation -->

### For developers

<!--- sec-begin-installation-dev -->

For development, we rely on [poetry](https://python-poetry.org) for all our
dependency management. To get started, you will need to make sure that poetry
is installed
([instructions here](https://python-poetry.org/docs/#installing-with-the-official-installer),
we found that pipx and pip worked better to install on a Mac).

For all of work, we use our `Makefile`.
You can read the instructions out and run the commands by hand if you wish,
but we generally discourage this because it can be error prone.
In order to create your environment, run `make virtual-environment`.

If there are any issues, the messages from the `Makefile` should guide you
through. If not, please raise an issue in the
[issue tracker](https://github.com/znicholls/gegca/issues).

For the rest of our developer docs, please see [](development-reference).

<!--- sec-end-installation-dev -->
