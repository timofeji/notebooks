
import base64
import io
import os
import re
import ast
import matplotlib as mpl
import matplotlib.pyplot as plt

from pathlib import Path
from collections import defaultdict
from core import *

import nbformat
from nbconvert.exporters.html import HTMLExporter

from jinja2 import FileSystemLoader
from traitlets.config import Config

from nb_processors import PostSettingsPreprocessor

TEMPLATE_FILE = 'post.html'



c = Config()
nb_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
nb_env = PathAwareEnvironment(
    loader=nb_loader,
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)



html_exporter = HTMLExporter(
    config=c, 
    extra_loaders=[nb_loader],
    environment = nb_env
    )
html_exporter.template_file = TEMPLATE_FILE
html_exporter.exclude_input_prompt = True  
html_exporter.exclude_output_prompt = True  
html_exporter.register_preprocessor(PostSettingsPreprocessor(), enabled=True)
html_exporter.mathjax_url = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS_HTML"


def search_notebooks(root_dir):
    """Recursively search for .ipynb files in the root directory."""
    notebooks = defaultdict(list)  # Maps category (directory) to a list of notebook paths
    for root, dirs, files in os.walk(NOTEBOOK_DIR):
        for file in files:
            if file.endswith('.ipynb'):
                notebook_path = Path(root) / file
                # Use the relative path to the root directory as the category
                category = Path(root).relative_to(NOTEBOOK_DIR)
                notebooks[category].append(notebook_path)
    return notebooks


def generate_notebook_page(n_src_file, output_dir):
    """Convert a notebook to HTML using nbconvert."""

     # Load the notebook
    with open(n_src_file, "r", encoding="utf-8") as f:
        notebook_content = nbformat.read(f, as_version=4)
 
    rel_path = output_dir.relative_to(OUTPUT_DIR)
    depth = len(rel_path.parts)
    
    
    html_exporter.environment.globals['url'] = '../' * depth

    print(f"Generating NoteBook: {n_src_file}")
    notebook_html, resources = html_exporter.from_notebook_node(notebook_content)
    
    settings = resources['post_settings']


    if not isinstance(settings, dict):
        print(f"ERROR: {n_src_file} doesn't have valid POST_SETTINGS dict")
        return ""
    

    output_file = output_dir / f"{n_src_file.stem}.html"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the rendered HTML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(notebook_html)

    return output_file, settings
