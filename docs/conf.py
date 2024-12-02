# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config
import os
import sys
import csv
from pathlib import Path

# The full version, including alpha/beta/rc tags
from sammi import __version__
from sammi.cdf_attribute_manager import CdfAttributeManager

sys.path.insert(0, os.path.abspath(".."))
# -- Project information -----------------------------------------------------

project = "sammi"
copyright = "No rights reserved"
author = "SAMMI Team"

version = __version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.mathjax",
    "sphinx_automodapi.automodapi",
    "sphinx_automodapi.smart_resolver",
    "sphinx_copybutton",
]

# Set automodapi to generate files inside the generated directory
automodapi_toctreedirnm = "generated/api"

# -- Generate CSV Files for Docs ---------------------------------------------
if not os.path.exists("generated"):
    os.mkdir("generated")  # generate the directory before putting things in it


def to_csv(info: dict, path: Path):
    # Get Header
    header_set = set()
    for attr_details in info.values():
        header_set.update(attr_details.keys())
    headers = ["Attribute"] + sorted(header_set)

    # Open the output file in write mode
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(headers)

        # Iterate over the dictionary and write each row
        for attr_name, attr_details in info.items():
            row = [attr_name]
            for key in headers[1:]:  # Skip "Attribute" which is already added
                row.append(attr_details.get(key, ""))
            # Write the row to the CSV
            writer.writerow(row)


# Global Attributes to CSV
global_info = CdfAttributeManager().global_attribute_info()
to_csv(global_info, Path("./generated/global_attributes.csv"))

# Variable Attributes to CSV
variable_info = CdfAttributeManager().variable_attribute_info()
to_csv(variable_info, Path("./generated/variable_attributes.csv"))

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The reST default role (used for this markup: `text`) to use for all
# documents. Set to the "smart" one.
default_role = "obj"

# Disable having a separate return type row
napoleon_use_rtype = False

# Disable google style docstrings
napoleon_google_docstring = False

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": (
        "https://docs.python.org/3/",
        (None, "http://data.astropy.org/intersphinx/python3.inv"),
    ),
    "sunpy": ("https://docs.sunpy.org/en/stable/", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "bizstyle"
html_static_path = ["_static"]

html_logo = "logo/sammi_logo.png"
html_favicon = "logo/favicon.ico"
html_css_files = [
    "css/custom.css",
]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Render inheritance diagrams in SVG
graphviz_output_format = "svg"

graphviz_dot_args = [
    "-Nfontsize=10",
    "-Nfontname=Helvetica Neue, Helvetica, Arial, sans-serif",
    "-Efontsize=10",
    "-Efontname=Helvetica Neue, Helvetica, Arial, sans-serif",
    "-Gfontsize=10",
    "-Gfontname=Helvetica Neue, Helvetica, Arial, sans-serif",
]
