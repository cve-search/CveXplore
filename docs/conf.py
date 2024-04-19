# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# import os
import string

# import sys
import typing

import docutils
import sphinx
import sphinx.domains.python
import sphinx.environment
import sphinx.util.logging
import sphinx.util.typing
from sphinx.util.docutils import SphinxRole
from sphinx_immaterial.apidoc import (
    object_description_options as _object_description_options,
)

# sys.path.insert(0, os.path.abspath("."))


logger = sphinx.util.logging.getLogger(__name__)


project = "CveXplore"
copyright = "2020, Paul Tikken"
author = "Paul Tikken"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_immaterial",
    "sphinx_immaterial.apidoc.python.apigen",
    "sphinx_immaterial.apidoc.format_signatures",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx_click",
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
.. role:: python(code)
   :language: python
   :class: highlight
"""

python_apigen_rst_prolog = """
.. default-role:: py:obj

.. default-literal-role:: python

.. highlight:: python
"""

object_description_options = []

object_description_options.append(("py:.*", dict(wrap_signatures_with_css=True)))
object_description_options.append(
    (
        "std:confval",
        dict(
            toc_icon_class="data", toc_icon_text="C", generate_synopses="first_sentence"
        ),
    )
)

object_description_options.append(
    (
        "std:objconf",
        dict(
            toc_icon_class="data",
            toc_icon_text="O",
            generate_synopses=None,
        ),
    )
)

object_description_options.append(
    (
        "std:themeconf",
        dict(
            toc_icon_class="data", toc_icon_text="T", generate_synopses="first_sentence"
        ),
    )
)

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


def _validate_parallel_build(app):
    # Verifies that all the extensions defined by this theme support parallel building.
    assert app.is_parallel_allowed("read")
    assert app.is_parallel_allowed("write")


if sphinx.version_info >= (6, 1):
    stringify = sphinx.util.typing.stringify_annotation
else:
    stringify = sphinx.util.typing.stringify


def _parse_object_description_signature(
    env: sphinx.environment.BuildEnvironment, signature: str, node: docutils.nodes.Node
) -> str:
    registry = _object_description_options.get_object_description_option_registry(
        env.app
    )
    registry_option = registry.get(signature)
    node += sphinx.addnodes.desc_name(signature, signature)
    if registry_option is None:
        logger.error("Invalid object description option: %r", signature, location=node)
    else:
        node += sphinx.addnodes.desc_sig_punctuation(" : ", " : ")
        annotations = sphinx.domains.python._parse_annotation(
            stringify(registry_option.type_constraint), env
        )
        node += sphinx.addnodes.desc_type("", "", *annotations)
        node += sphinx.addnodes.desc_sig_punctuation(" = ", " = ")
        default_repr = repr(registry_option.default)
        node += docutils.nodes.literal(
            default_repr,
            default_repr,
            language="python",
            classes=["python", "code", "highlight"],
        )
    return signature


def _parse_confval_signature(
    env: sphinx.environment.BuildEnvironment, signature: str, node: docutils.nodes.Node
) -> str:
    values = env.config.values
    registry_option = values.get(signature)
    node += sphinx.addnodes.desc_name(signature, signature)
    if registry_option is None:
        logger.error("Invalid config option: %r", signature, location=node)
    else:
        default, rebuild, types = registry_option
        if isinstance(types, sphinx.config.ENUM):
            types = (typing.Literal[tuple(types.candidates)],)
        if isinstance(types, type):
            types = (types,)
        if types:
            type_constraint = typing.Union[tuple(types)]
            node += sphinx.addnodes.desc_sig_punctuation(" : ", " : ")
            annotations = sphinx.domains.python._parse_annotation(
                stringify(type_constraint), env
            )
            node += sphinx.addnodes.desc_type("", "", *annotations)
        if not callable(default):
            node += sphinx.addnodes.desc_sig_punctuation(" = ", " = ")
            default_repr = repr(default)
            node += docutils.nodes.literal(
                default_repr,
                default_repr,
                language="python",
                classes=["python", "code", "highlight"],
            )
    return signature


class TestColor(SphinxRole):
    color_type: str
    style = (
        "background-color: %s;"
        "color: %s;"
        "padding: 0.05rem 0.3rem;"
        "border-radius: 0.25rem;"
        "cursor: pointer;"
    )
    style_params: typing.Tuple[str, str]
    on_click = (
        "document.body.setAttribute(`data-md-color-$color_type`, `$attr`);"
        "var name = document.querySelector("
        "`#$color_type-color-conf-example code span:nth-last-child(3)`);"
        "name.textContent = `&quot;$attr&quot;`;"
    )

    def run(self):
        if self.color_type == "primary":
            self.style_params = (
                f"var(--md-{self.color_type}-fg-color)",
                f"var(--md-{self.color_type}-bg-color)",
            )
        elif self.color_type == "accent":
            self.style_params = (
                "var(--md-code-bg-color)",
                f"var(--md-{self.color_type}-fg-color)",
            )
        color_attr = ""
        if self.color_type in ("primary", "accent"):
            color_attr = f'data-md-color-{self.color_type}="{self.text}"'
        el_style = self.style % self.style_params
        click_func = string.Template(self.on_click).substitute(
            color_type=self.color_type, attr=self.text
        )
        node = docutils.nodes.raw(
            self.rawtext,
            f"<button {color_attr} style="
            f'"{el_style}" onclick="{click_func}">{self.text}</button>',
            format="html",
        )
        return ([node], [])


class TestColorPrimary(TestColor):
    color_type = "primary"


class TestColorAccent(TestColor):
    color_type = "accent"


class TestColorScheme(TestColor):
    color_type = "scheme"
    style_params = ("var(--md-primary-fg-color)", "var(--md-primary-bg-color)")
    on_click = (
        "document.body.setAttribute('data-md-color-switching', '');"
        + TestColor.on_click
        + "setTimeout(function() {document.body.removeAttribute"
        "('data-md-color-switching')});"
    )


def setup(app):
    app.add_role("test-color-primary", TestColorPrimary())
    app.add_role("test-color-accent", TestColorAccent())
    app.add_role("test-color-scheme", TestColorScheme())

    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
        parse_node=_parse_confval_signature,
    )

    app.add_object_type(
        "themeconf",
        "themeconf",
        objname="theme configuration option",
        indextemplate="pair: %s; theme option",
    )

    app.add_object_type(
        "objconf",
        "objconf",
        objname="object description option",
        indextemplate="pair: %s; object description option",
        parse_node=_parse_object_description_signature,
    )

    # Add `event` type from Sphinx's own documentation, to allow intersphinx
    # references to Sphinx events.
    app.add_object_type(
        "event",
        "event",
        objname="Sphinx event",
        indextemplate="pair: %s; event",
    )
    app.connect("builder-inited", _validate_parallel_build)
