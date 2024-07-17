# Configuration file for the Sphinx documentation builder.
#
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from ibpmodel import __version__ as ibp_version

project = 'ibpmodel'
copyright = '2023, Ina Rusch'
author = 'Ina Rusch'
version = ibp_version
release = ibp_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.duration',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autorun'
]
#extensions.append('sphinx_autorun')
templates_path = ['_templates']
exclude_patterns = []
autodoc_mock_imports = ['numpy', 'pandas', 'cdflib','matplotlib','scipy']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_show_sourcelink = False
html_theme_options = {
    'display_version': True,
    'navigation_depth': 5,
}
