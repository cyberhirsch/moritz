# Moritz manual, built with Sphinx.
project = "Moritz Manual"
author = "Moritz Authors"
copyright = "2026, Moritz Authors (CC-BY-SA 4.0)"
version = "0.3"
release = "0.3 (in progress)"

extensions = ["sphinx.ext.extlinks"]
extlinks = {
    # A page of Blender's manual, for everything Moritz leaves as it is.
    "blender": ("https://docs.blender.org/manual/en/latest/%s", "%s"),
}

html_theme = "furo"
html_title = "Moritz Manual"
html_static_path = []
html_show_sourcelink = False
html_theme_options = {
    "source_repository": "https://github.com/cyberhirsch/moritz/",
    "source_branch": "moritz/main",
    "source_directory": "moritz/manual/",
}
exclude_patterns = ["_build", "README.md"]
