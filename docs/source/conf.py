# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

from hawkmoth.util import readthedocs
readthedocs.clang_setup()

sys.path.insert(0, os.path.abspath('../..'))
sys.path.append(os.path.abspath('sphinxext'))


autodoc_mock_imports = ['numpy', 'matplotlib', 'matplotlib.pyplot',
                'mpl_toolkits.axes_grid1', 'scipy', 'scipy.optimize',
                'matplotlib.animation', 'numpy.random', 'scipy.stats']

# for mod_name in MOCK_MODULES:
#     sys.modules[mod_name] = mock.Mock()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'dfmcontrol'
copyright = '2023, Adrian van Eik'
author = 'Adrian van Eik'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon',
              'sphinx.ext.autosectionlabel','sphinx.ext.intersphinx', 'hawkmoth']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
