# -*- coding: utf-8 -*-
import os, datetime, time
from importlib import metadata

intersphinx_mapping = {
    'python': ('http://docs.python.org', None),
}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    ]

# General
source_suffix = '.rst'
master_doc = 'index'
project = 'manipulate'
first_year = 2024
current_year = datetime.datetime.now().year
copyright = (str(current_year) if current_year==first_year else ('%s-%s'%(first_year,current_year)))+' Chris Withers'
version = release = metadata.version(project)
exclude_trees = ['_build']
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'furo'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Chris Withers', 'manual'),
]

exclude_patterns = ['_build', '**/furo.js.LICENSE.txt']

nitpicky = True
nitpick_ignore = [
]
