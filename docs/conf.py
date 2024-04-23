import collections
import json
import os
import string
import sys
import typing

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

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
from setuptools import find_packages
from pkgutil import iter_modules

os.environ["DOC_BUILD"] = json.dumps({"DOC_BUILD": "YES"})
os.environ["DATASOURCE_TYPE"] = "mysql"
os.environ["DATASOURCE_PROTOCOL"] = "mysql"
os.environ["DATASOURCE_DBAPI"] = "pymysql"

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
    "sphinx_sqlalchemy",
]

default_role = "any"
autosectionlabel_prefix_document = True
show_warning_types = True
suppress_warnings = [
    "ref.ref",
    "ref.doc",
    "ref.term",
    "misc.highlighting_failure",
    "toc.excluded",
]

autoclass_content = "both"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

python_apigen_modules = {
    "CveXplore": "CveXplore/main/",
}

python_apigen_ban_list = ["cli_cmds", "celery_app", "database_models"]

python_apigen_default_groups = [
    ("class:.*", "Classes"),
    (r".*:.*\.__(init|new)__", "Constructors"),
    (r".*:.*\.__(eq|ne|ge|gt|le|lt)__", "Comparison operators"),
    (r".*:.*\.__(reduce)__", "Helper methods"),
    (r".*:.*\.__(next|iter)__", "Iterators"),
    (r".*:.*\.__(str|repr)__", "String representation"),
]

python_apigen_default_order = [
    ("class:.*", -10),
    (r".*\.__(init|new)__", -5),
    (r".*\.__(eq|ne|ge|gt|le|lt)__", 8),
    (r".*\.__(reduce)__", 7),
    (r".*\.__(next|iter)__", 9),
    (r".*\.__(str|repr)__", 10),
]

python_type_aliases = {
    "CveXplore.api.helpers.cve_search_api.ApiBaseClass": "ApiBaseClass",
    "CveXplore.database.connection.base.db_connection_base.DatabaseConnectionBase": "DatabaseConnectionBase",
    "CveXplore.core.database_maintenance.download_handler.ABC": "ABC",
    "CveXplore.objects.cvexplore_object.CveXploreObject": "CveXploreObject",
    "CveXplore.core.celery_task_handler.task_handler.RedBeatSchedulerEntry": "RedBeatSchedulerEntry",
    "celery.beat.ScheduleEntry": "ScheduleEntry",
    "CveXplore.errors.tasks.TaskError": "TaskError",
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


def _find_modules(module_path):
    # module_path = os.path.dirname(module_name.__file__)
    pkg_name = module_path.split(os.path.sep)[-1]
    modules = set()
    for pkg in find_packages(module_path):
        modules.add(pkg)
        pkgpath = module_path + "/" + pkg.replace(".", "/")
        if sys.version_info.major == 2 or (
            sys.version_info.major == 3 and sys.version_info.minor < 6
        ):
            for _, name, ispkg in iter_modules([pkgpath]):
                if not ispkg:
                    modules.add(pkg + "." + name)
        else:
            for info in iter_modules([pkgpath]):
                if not info.ispkg:
                    modules.add(pkg + "." + info.name)
    # return pkg_name, modules
    # pkg_name, packages = find_modules(CveXplore)
    data = sorted(modules)

    ret_dict = collections.defaultdict(list)

    for each in data:
        if "." in each:
            ret_dict[each.split(".")[0]].append(f"{pkg_name}.{each}")
        else:
            continue

    ret_dict = dict(ret_dict)

    package_dict = {}

    for k, v in ret_dict.items():
        if k not in python_apigen_ban_list:
            for mod_name in v:
                package_dict[mod_name] = f"{pkg_name}/{k}/"

    return package_dict


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


def _parse_config_values(app, config_class):

    logger.info(f"Parsing config values for {config_class}")

    all_configs = [c for c in dir(config_class) if not c.startswith("_")]

    for each in all_configs:
        logger.info(
            f"Value {each}; default: {getattr(config_class, each)}, type: {type(getattr(config_class, each))}"
        )
        app.add_config_value(
            name=each,
            default=getattr(config_class, each),
            rebuild="html",
            types=[type(getattr(config_class, each))],
        )

    logger.info("Done Parsing config variables!!")


def setup(app):
    python_apigen_modules.update(_find_modules("../CveXplore"))

    from CveXplore.common.config import Configuration

    config = Configuration()

    _parse_config_values(app, config)

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
