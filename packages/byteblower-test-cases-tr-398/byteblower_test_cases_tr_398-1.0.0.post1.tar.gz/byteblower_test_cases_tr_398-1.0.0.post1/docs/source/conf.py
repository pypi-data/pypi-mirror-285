# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from datetime import date

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

project = 'ByteBlower TR-398 Test Case'
copyright = f'{date.today().year!s}, Excentis NV'
author = 'Excentis NV'

# The full version, including alpha/beta/rc tags
release = metadata.version('byteblower-test-cases-tr-398')

# The short X.Y version
# for example take major/minor
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.imgmath',
    'sphinx.ext.extlinks',
    'sphinx_rtd_theme',
    'sphinx_tabs.tabs',
    'sphinx-jsonschema',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_include/*.rst',
]

# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    "logo_only": False,
    "style_external_links": True,
    "style_nav_header_background": "#00aeef"
}

# The name of the Pygments (syntax highlighting) style to use.
# XXX - Changes e.g. background on `code-block`s.
pygments_style = 'sphinx'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# A list of CSS files. The entry must be a filename string or a tuple
# containing the filename string and the attributes dictionary.
# The filename must be relative to the html_static_path, or a full URI
# with scheme like https://example.org/style.css.
# The attributes is used for attributes of <link> tag.
# It defaults to an empty list.
html_css_files = ['excentis.css']

# If true, “Created using Sphinx” is shown in the HTML footer.
# Default is True.
html_show_sphinx = False

# If true, the reST sources are included in the HTML build as _sources/name.
# The default is True.
html_copy_source = False

# If true (and html_copy_source is true as well), links to the reST sources
# will be added to the sidebar. The default is True.
html_show_sourcelink = False

# A list of paths that contain extra files not directly related to the
# documentation, such as robots.txt or .htaccess. Relative paths are taken
# as relative to the configuration directory. They are copied to the output
# directory. They will overwrite any existing file of the same name.
#
# As these files are not meant to be built, they are automatically excluded
# from source files.
html_extra_path = [
    # NOTE: The extra 'test-cases/tr-398' sub-directory is important
    #       for including this documentation in the ByteBlower Test Framework
    #       "overview" documentation (``byteblower-test-framework-docs``)
    'extra/test-cases/tr-398',
]

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

# If true, `todo` and `todoList` produce output, else they produce nothing.
# todo_include_todos = True  # For development/beta releases!
todo_include_todos = False  # Only for release!

# If this is True, todolist produce output without file path and line, The default is False.
todo_link_only = True  # New in version 1.4

# -- Options for sphinx-tabs extension ----------------------------------------------
# https://sphinx-tabs.readthedocs.io/en/latest/#sphinx-configuration

# By default, tabs can be closed by selecting the open tab. This functionality
# can be disabled using:
sphinx_tabs_disable_tab_closing = True

# By default, the extension loads predefined CSS styles for tabs.
# To disable the CSS from loading, add the following:
# sphinx_tabs_disable_css_loading = True
