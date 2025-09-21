# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.setrecursionlimit(2500)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SkyTracker'
copyright = '2025, Jasper Jeuken'
author = 'Jasper Jeuken'
release = '0.1.0'
today_fmt = '%-d %B %Y at %H:%M'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx_toolbox.sidebar_links',
    'sphinx_toolbox.github',
    'sphinx_toolbox.more_autodoc.overloads',
    'sphinx_design'
]

autosummary_generate = True
autodoc_default_options = {
    'inherited-members': False
}
autodoc_member_order = 'groupwise'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

github_username = 'JasperJeuken'
github_repository = 'SkyTracker'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'globaltoc.html'
    ]
}
html_theme_options = {
    'show_prev_next': False,
    "secondary_sidebar_items": [],
    "logo": {
        "text": "SkyTracker documentation",
        "image_light": "_static/logo.svg",
        "image_dark": "_static/logo.svg",
    }
}
html_last_updated_fmt = '%b %d, %Y'
html_show_sphinx = False
html_favicon = '_static/logo.ico'
