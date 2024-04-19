# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "CveXplore"
copyright = "2020, Paul Tikken"
author = "Paul Tikken"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_immaterial",
    "sphinx_immaterial.apidoc.python.apigen",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
]

default_role = "any"
autosectionlabel_prefix_document = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

python_apigen_modules = {
    "CveXplore": "CveXplore/main/",
    "CveXplore.api.connection.api_db": "CveXplore/api/",
    "CveXplore.api.helpers.cve_search_api": "CveXplore/api/",
    "CveXplore.objects.cvexplore_object": "CveXplore/objects/",
}

python_apigen_default_groups = [
    ("class:.*", "Classes"),
    (r".*:.*\.__(init|new)__", "Constructors"),
    (r".*:.*\.__eq__", "Comparison operators"),
    (r".*:.*\.__(str|repr)__", "String representation"),
]

python_apigen_default_order = [
    ("class:.*", -10),
    (r".*\.__(init|new)__", -5),
    (r".*\.__(str|repr)__", 5),
]

python_type_aliases = {
    "CveXplore.api.helpers.cve_search_api.ApiBaseClass": "ApiBaseClass",
}

python_apigen_order_tiebreaker = "alphabetical"

rst_prolog = """
.. role python(code)
   :language: python
   :class: highlight
"""

python_apigen_rst_prolog = """
.. default-role:: py:obj

.. default-literal-role:: python

.. highlight:: python
"""

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_css_files = ["custom.css"]
html_last_updated_fmt = ""
html_title = "CveXplore"
html_favicon = "_static/images/CveExplore_icon.png"
html_logo = "_static/images/CveExplore_icon.png"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_immaterial"
html_static_path = ["_static"]

html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
        "edit": "material/file-edit-outline",
    },
    "site_url": "https://cve-search.github.io/CveXplore/",
    "repo_url": "https://github.com/cve-search/CveXplore",
    "repo_name": "CveXplore",
    "edit_uri": "blob/master/docs",
    "toc_title_is_page_title": True,
    "features": [
        "navigation.expand",
        # "navigation.tabs",
        # "toc.integrate",
        "navigation.sections",
        # "navigation.instant",
        # "header.autohide",
        "navigation.top",
        # "navigation.tracking",
        # "search.highlight",
        "search.share",
        "toc.follow",
        "toc.sticky",
        "content.tabs.link",
        "announce.dismiss",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "blue-grey",
            "accent": "light-blue",
            "toggle": {
                "icon": "material/lightbulb-outline",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "blue-grey",
            "accent": "lime",
            "toggle": {
                "icon": "material/lightbulb",
                "name": "Switch to light mode",
            },
        },
    ],
}
