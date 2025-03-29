from collections import defaultdict
import os
import subprocess
import shutil
from pathlib import Path

from nbconvert import HTMLExporter
import nbformat

ROOT_DIR = Path('./src')  # The root directory to search for notebooks
OUTPUT_DIR = Path('./build')  # Directory to store the generated blog posts
TEMPLATE_DIR = Path('./resources/')  # Path to the custom nbconvert template
CSS_FILE = Path('./resources/styles.css')  # Path to the CSS file

def search_notebooks(root_dir):
    """Recursively search for .ipynb files in the root directory."""
    notebooks = defaultdict(list)  # Maps category (directory) to a list of notebook paths
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith('.ipynb'):
                notebook_path = Path(root) / file
                # Use the relative path to the root directory as the category
                category = Path(root).relative_to(ROOT_DIR)
                notebooks[category].append(notebook_path)
    return notebooks


def convert_notebook(n_src_file, output_dir, template_dir):
    """Convert a notebook to HTML using nbconvert."""

    # Run the conversion
    build_cmd = f'python -m nbconvert {str(n_src_file)} --to html'
    subprocess.run(build_cmd, check=True)

    output_file = f"{n_src_file.parent / n_src_file.stem}.html"
    shutil.move(output_file , f'{output_dir / n_src_file.stem}.html')

    return output_file

def render_notebook_to_html(notebook_path):
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = nbformat.read(f, as_version=4)
        
        html_exporter = HTMLExporter()
        body, _ = html_exporter.from_notebook_node(notebook_content)
        return body
    except nbformat.reader.NotJSONError:
        print(f"Warning: {notebook_path} is not a valid notebook (NotJSONError). Skipping this file.")
        return ""
    except Exception as e:
        print(f"Error: Failed to process {notebook_path}. Reason: {str(e)}")
        return ""

def generate_categories(category, notebooks, output_dir):
    """Generate a category page with links to notebooks."""
    category_page_content = f"""
    <html>
    <head>
        <title>{category}</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #007bff; }}
            .post-link {{ font-size: 1.2em; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <h1>{category}</h1>
        <ul>
    """
    
    # Add links to each notebook in the category
    for notebook in notebooks:
        post_html = output_dir / f"{notebook.stem}.html"
        category_page_content += f'<li><a href="{post_html.name}" class="post-link">{notebook.stem}</a></li>\n'
    
    category_page_content += """
        </ul>
    </body>
    </html>
    """
    
    category_page_path = output_dir / f"{category}.html"
    with open(category_page_path, 'w') as f:
        f.write(category_page_content)
    
    print(f"Category page generated at {category_page_path}")

def generate_homepage(notebooks_by_category, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Start the HTML document
    html_content = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My Blog</title>
        <link rel="stylesheet" href="styles.css">
        <script src="script.js"></script>
    </head>
    <body>

    <header>
        <h1>Timofej Jermolaev</h1>
    </header>

    <nav>
    '''

    # Loop through all directories and files in the root directory
    category_links = ["Home", "Publications", "Portfolio"]
    section_html = ""

    # Join category links and add to the navigation
    html_content += "\n".join(category_links)
    html_content += "</nav>\n"
    
    # Add the main content (categories/sections)
    html_content += section_html

    # Footer
    html_content += '''
    <footer>
        <p>&copy; 2025 My Blog | <a href="#">Privacy Policy</a></p>
    </footer>

</body>
</html>'''

    # Write the final HTML file to the output directory
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Site successfully built at {output_dir}/index.html")
 


def main():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    shutil.copy(CSS_FILE, OUTPUT_DIR / CSS_FILE.name)

    notebooks_by_category = search_notebooks(ROOT_DIR)
    for category, notebooks in notebooks_by_category.items():
        category_output_dir = OUTPUT_DIR / category
        category_output_dir.mkdir(parents=True, exist_ok=True)
        
        # for n in notebooks:
        #     convert_notebook(n, category_output_dir, TEMPLATE_DIR)
        
    
   
    generate_homepage(notebooks, OUTPUT_DIR)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--config', type=str, default="default", help='configuration for setup')
    # parser.set_defaults()
    # cfg = parser.parse_args()

    # if cfg.watch:
    main()
