import os
import shutil

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "asv_runner"
copyright = "2023--present, asv Developers"
author = "asv Developers"
release = "0.2.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "autodoc2",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx_contributors",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.spelling",
]

autodoc2_render_plugin = "myst"
autodoc2_packages = [
    "../../asv_runner",
]

myst_enable_extensions = [
    "deflist",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "asv": ("https://asv.readthedocs.io/en/latest/", None),
}

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "source_repository": "https://github.com/HaoZeke/asv_runner/",
    "source_branch": "main",
    "source_directory": "docs/",
}


# ------------- Copying things
docs_source_dir = os.path.abspath(os.path.dirname(__file__))
project_root_dir = os.path.abspath(os.path.join(docs_source_dir, "..", ".."))
changelog_src = os.path.join(project_root_dir, "CHANGELOG.md")
changelog_dest = os.path.join(docs_source_dir, "CHANGELOG.md")
shutil.copyfile(changelog_src, changelog_dest)
