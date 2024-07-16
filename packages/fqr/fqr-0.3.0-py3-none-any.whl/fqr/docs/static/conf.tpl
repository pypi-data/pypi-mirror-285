"""
Sphinx [configuration file](https://www.sphinx-doc.org/en/master/usage/configuration.html).

---

_Automatically generated by fqr._

"""

import commonmark
import os
import typing

if typing.TYPE_CHECKING:
    import sphinx.application

    What = (
        typing.Literal['module']
        | typing.Literal['class']
        | typing.Literal['exception']
        | typing.Literal['function']
        | typing.Literal['method']
        | typing.Literal['attribute']
        )


    class SupportsOptions(typing.Protocol):
        """
        Any object with `bool` attributes:

        * inherited_members
        * undoc_members
        * show_inheritance

        Each attribute defaults to `True` if the flag option \
        of same name was given to the auto directive.

        """

        inherited_members: bool
        undoc_members: bool
        show_inheritance: bool


class Constants:
    """Constant values specific to sphinx conf.py files."""

    STATIC_PATH_REF = '_static'


def docstring(
    app: sphinx.application.Sphinx,
    what: What,
    name: str,
    obj: typing.Any,
    options: SupportsOptions,
    lines: typing.Iterable[str],
    ) -> None:
    """
    Parse markdown in [docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#docstring-preprocessing).

    ---

    Emitted when autodoc has read and processed a docstring. \
    `lines` is a list of strings – the lines of the processed \
    docstring – that the event handler can modify **in place** \
    to change what Sphinx puts into the output.

    """

    md = '\n'.join(lines)
    ast = commonmark.Parser().parse(md)
    rst: str = commonmark.ReStructuredTextRenderer().render(ast)
    lines[:] = rst.splitlines()

    return None


def setup(app: sphinx.application.Sphinx) -> None:
    """Generate documentation."""

    app.connect('autodoc-process-docstring', docstring)

    return None


root_doc = project = '${package_name}'
version = release = '${package_version}'
author = copyright = '${author_name}'

add_module_names = ${add_module_names}
autodoc_inherit_docstrings = ${autodoc_inherit_docstrings}
autodoc_default_options = {
    'member-order': 'bysource',
    }

extensions = [
    'sphinx.ext.autodoc',
    ]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_favicon = os.path.join('.', Constants.STATIC_PATH_REF, 'favicon.ico')
html_logo = os.path.join('.', Constants.STATIC_PATH_REF, 'logo.png')
html_theme = '${sphinx_theme}'
html_static_path = [Constants.STATIC_PATH_REF]
