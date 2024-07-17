# pyconverters_ocrmypdf

[![license](https://img.shields.io/github/license/oterrier/pyconverters_ocrmypdf)](https://github.com/oterrier/pyconverters_ocrmypdf/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyconverters_ocrmypdf/workflows/tests/badge.svg)](https://github.com/oterrier/pyconverters_ocrmypdf/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyconverters_ocrmypdf)](https://codecov.io/gh/oterrier/pyconverters_ocrmypdf)
[![docs](https://img.shields.io/readthedocs/pyconverters_ocrmypdf)](https://pyconverters_ocrmypdf.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyconverters_ocrmypdf)](https://pypi.org/project/pyconverters_ocrmypdf/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyconverters_ocrmypdf)](https://pypi.org/project/pyconverters_ocrmypdf/)

Convert OCRized PDF to text using [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF)

## Installation

You can simply `pip install pyconverters_ocrmypdf`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyconverters_ocrmypdf
```

### Running the test suite

You can run the full test suite against all supported versions of Python (3.8) with:

```
tox
```

### Building the documentation

You can build the HTML documentation with:

```
tox -e docs
```

The built documentation is available at `docs/_build/index.html.
