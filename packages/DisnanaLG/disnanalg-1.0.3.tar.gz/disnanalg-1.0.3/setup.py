# Author: Kenta Nakamura <support@disnana.com>
# Copyright (c) 2021-2024 tp-link
# License: BSD 3 clause

from setuptools import setup
import DisnanaLG

DESCRIPTION = "seaborn-analyzer: data visualization of regression, classification and distribution"
NAME = 'DisnanaLG'
AUTHOR = 'Disnana'
AUTHOR_EMAIL = 'support@disnana.com'
LICENSE = 'BSD 3-Clause'
VERSION = "1.0.3"
PYTHON_REQUIRES = ">=3.6"

INSTALL_REQUIRES = [
]

EXTRAS_REQUIRE = {
}

PACKAGES = [
    'DisnanaLG'
]

CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3 :: Only'
]

with open('README.rst', 'r', encoding="utf-8") as fp:
    long_description = fp.read()

setup(name=NAME,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=AUTHOR,
      maintainer_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      long_description=long_description,
      license=LICENSE,
      version=VERSION,
      python_requires=PYTHON_REQUIRES,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      packages=PACKAGES,
      classifiers=CLASSIFIERS
      )
