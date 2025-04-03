
import base64
import io
import os
import re
import matplotlib as mpl
import matplotlib.pyplot as plt

from pathlib import Path
from collections import defaultdict
from core import *

import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import Preprocessor

class NavigationMenuPreprocessor(Preprocessor):
    """
    A preprocessor that creates a navigation menu based on Markdown headers.
    The menu links will scroll the view to the respective headers when clicked.
    """
    
    def preprocess(self, nb, resources):
        """
        Scans the notebook for Markdown cells with headers,
        builds a navigation menu, and adds it to the notebook.
        """
        # Extract headers from markdown cells
        headers = []

        for cell_idx, cell in enumerate(nb.cells):
            if cell.get('cell_type') == 'markdown':
                # Find all headers in markdown
                header_pattern = re.compile(r'^(#{1,6})\s+(.+?)(?:\s+\{#([^}]+)\})?$', re.MULTILINE)
                for match in header_pattern.finditer(cell.get('source')):
                    level = len(match.group(1))
                    title = match.group(2).strip()
                    # Use custom id if provided, otherwise generate from title
                    anchor_id = match.group(3) if match.group(3) else title.lower().replace(' ', '-')
                    anchor_id = re.sub(r'[^\w-]', '', anchor_id)
                    
                    headers.append({
                        'level': level,
                        'title': title,
                        'id': anchor_id,
                        'cell_idx': cell_idx
                    })
        
        # Generate navigation menu HTML
        if headers:
            nav_html = self._create_navigation_html(headers)
            
            # Insert navigation menu as the first cell
            nav_cell = {
                'cell_type': 'markdown',
                'metadata': {},
                'source': nav_html
            }
            
            nb.cells.insert(0, nav_cell)
            
            # Update header cells to include proper anchors
            self._add_header_anchors(nb, headers)
        
        return nb, resources
    
    def _create_navigation_html(self, headers):
        """
        Create the HTML for the navigation menu based on extracted headers.
        """
        nav_md = ""
        nav_md += f"""<div class='nb-nav-menu hidden' id='navMenu'>
                      <h1>Table of Contents:</h1>
                      <ul>"""

        for header in headers:
            # Indent based on header level
            nav_md += f"<li>"
            indent = "  " * (header['level'] - 1)
            nav_md += f"<a href={header['id']}>{indent}{header['title']}</a>"
            nav_md += f"</li>"

        nav_md += f"</ul>"
        nav_md += "</div>\n\n---\n"
        
        return nav_md
    
    def _add_header_anchors(self, nb, headers):
        """
        Update markdown cells to include anchors for headers.
        """
        for header in headers:
            cell = nb.cells[header['cell_idx']]
            if cell.get('cell_type') == 'markdown':
                # Find and replace the header with an anchored version
                header_pattern = re.compile(r'^(#{1,6}\s+' + re.escape(header['title']) + r')(?:\s+\{#[^}]+\})?$', re.MULTILINE)
                replacement = r'\1 {#' + header['id'] + '}'
                cell['source'] = header_pattern.sub(replacement, cell.get('source'))
    
class LightDarkMatplotlibPreprocessor(Preprocessor):
    def preprocess(self, nb, resources):
        for cell in nb.cells:
            if cell.get('cell_type') == "code" and "outputs" in cell:
                for output in cell.outputs:
                    if output.output_type == "display_data" and "image/png" in output.data:
                        # Decode the original figure
                        img_data = base64.b64decode(output.data["image/png"])
                        img = plt.imread(io.BytesIO(img_data))

                        # Generate a light and dark version
                        light_img_data = self._render_matplotlib_image(img, "default")  # Light theme
                        dark_img_data = self._render_matplotlib_image(img, "dark_background")  # Dark theme

                        # Embed both versions in the output with theme-specific classes
                        output.data["text/html"] = f"""
                        <div class="figure">
                            <img class="light-theme" src="data:image/png;base64,{light_img_data}" />
                            <img class="dark-theme" src="data:image/png;base64,{dark_img_data}" />
                        </div>
                        """
                        # del output.data["image/png"]  # Remove original image to prevent duplication
        return nb, resources

    def _render_matplotlib_image(self, img, style):
        """Applies a Matplotlib style and returns a high-resolution base64-encoded PNG."""
        plt.style.use(style)
        fig = plt.figure()  # Increase DPI for better resolution
        plt.imshow(img)
        plt.axis("off")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, dpi=300)
        plt.close(fig)

        return base64.b64encode(buf.getvalue()).decode("utf-8") 

custom_latex_macros = r'''
    MathJax.Hub.Config({
        TeX: {
            Macros: {
                Iota: "{\mathbb{I}}"  // Define \Iota as a blackboard bold I
            }
        }
    });
'''

NOTEBOOK_TEMPLATE = 'template_earthpunk'

html_exporter = HTMLExporter()
html_exporter.register_preprocessor(LightDarkMatplotlibPreprocessor(), enabled=True)
html_exporter.register_preprocessor(NavigationMenuPreprocessor(), enabled=True)
html_exporter.template_name = 'full'  # Use basic template
html_exporter.exclude_input_prompt = True  # Remove input prompts
html_exporter.exclude_output_prompt = True  # Remove output prompts
html_exporter.template_data = {
    "mathjax_config": custom_latex_macros
}

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

def extract_notebook_content(html_content):
    """Extract just the notebook content from the full HTML document."""
    # Look for content between <body> and </body>
    body_match = re.search(r'<main>(.*?)</main>', html_content, re.DOTALL)
    if body_match:
        return body_match.group(1)
    return html_content  # Return original if extraction fails

def generate_notebook(n_src_file, output_dir, template_dir):
    """Convert a notebook to HTML using nbconvert."""

     # Load the notebook
    with open(n_src_file, "r", encoding="utf-8") as f:
        notebook_content = nbformat.read(f, as_version=4)
    
    # Convert the notebook to HTML
    notebook_html, _ = html_exporter.from_notebook_node(notebook_content)
    notebook_content_html = extract_notebook_content(notebook_html)
    
    rel_path = output_dir.relative_to(OUTPUT_DIR)
    depth = len(rel_path.parts)
    
    env.set_page_depth(depth)
    
    # Create a title from the notebook filename
    title = n_src_file.stem.replace('_', ' ').title()
    
    # Render the notebook content in the base template
    template = env.get_template('notebook.html')
    output_html = template.render(
        title = title,
        notebook_content = notebook_content_html,
        active_page='publications',  # Adjust based on your navigation structure
    )

    output_file = output_dir / f"{n_src_file.stem}.html"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the rendered HTML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_html)

    return output_file
