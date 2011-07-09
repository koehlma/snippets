# -*- coding: utf-8 -*-

import sys, os

doc_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(doc_directory, '..'))

import gplayer

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.intersphinx', 'sphinx.ext.todo']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'GPlayer'
copyright = u'2011, linuxmaxi'

version = gplayer.__version__
release = gplayer.__version__

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'default'

html_static_path = ['_static']

htmlhelp_basename = 'GPlayerdoc'

latex_documents = [
  ('index', 'GPlayer.tex', u'GPlayer Documentation',
   u'linuxmaxi', 'manual'),
]

man_pages = [
    ('index', 'gplayer', u'GPlayer Documentation',
     [u'linuxmaxi'], 1)
]


#intersphinx_mapping = {'http://docs.python.org/': None}
