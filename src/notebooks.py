
import os
import shutil
import subprocess

from pathlib import Path
from collections import defaultdict
from core import *

NOTEBOOK_TEMPLATE = 'template_earthpunk'

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

def generate_notebook(n_src_file, output_dir, template_dir):
    """Convert a notebook to HTML using nbconvert."""


    headings = extract_headings_from_notebook(n_src_file)

    subprocess.run([
        "python", "-m", "nbconvert", n_src_file, "--to", "html",
        f'--TemplateExporter.extra_template_basedirs={template_dir}',
        f'--template={NOTEBOOK_TEMPLATE}'
    ])

    output_file = f"{n_src_file.parent / n_src_file.stem}.html"
    shutil.move(output_file, f'{output_dir / n_src_file.stem}.html')


    return output_file



def extract_headings_from_notebook(notebook_path):
    """Extract headings from the notebook file using regex."""
    import json
    
    headings = []
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
        
        cells = notebook_content.get('cells', [])
        
        for cell in cells:
            if cell.get('cell_type') == 'markdown':
                source = ''.join(cell.get('source', []))
                
                # Find headings in markdown using regex
                for match in re.finditer(r'^(#{1,4})\s+(.+?)(?:\n|$)', source, re.MULTILINE):
                    level = len(match.group(1))
                    text = match.group(2).strip()
                    
                    # Generate an anchor ID from the heading text
                    anchor = re.sub(r'[^\w\s-]', '', text).lower()
                    anchor = re.sub(r'[-\s]+', '-', anchor).strip('-_')
                    
                    headings.append({
                        'level': level,
                        'text': text,
                        'anchor': anchor
                    })
    except Exception as e:
        print(f"Error extracting headings from {notebook_path}: {str(e)}")
    
    return headings

def generate_category_page(category, notebooks, output_dir):
    """Generate a category page with links to notebooks using Jinja template."""
    # Set page depth based on category (subdirectory level)
    depth = len(str(category).split('/')) if str(category) != '.' else 0
    env.set_page_depth(depth)
    
    notebook_links = []
    for notebook in notebooks:
        notebook_links.append({
            'title': notebook.stem.replace('_', ' ').title(),
            'url': f"{notebook.stem}.html"
        })
    
    template = env.get_template('category.html')
    category_html = template.render(
        category=str(category) if str(category) != '.' else 'Main Category',
        notebooks=notebook_links,
        active_page=''  # No active page for category pages
    )
    
    category_page_path = output_dir / f"{category}.html"
    with open(category_page_path, 'w') as f:
        f.write(category_html)

