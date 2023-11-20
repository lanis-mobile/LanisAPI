# Configuration file for the Sphinx documentation builder.

# -- Project information

project = "LanisAPI"
copyright = "2023, kurwjan"
author = "kurwjan"

release = "0.4.0a"
version = "0.4.0a"

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon"
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "furo"
html_title = "LanisAPI"

# -- don't show lanisapi.LanisClient at the beginning

add_module_names = False
