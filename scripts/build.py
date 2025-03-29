from collections import defaultdict
import os
import subprocess
import shutil
import jinja2
from pathlib import Path



ROOT_DIR = Path('./src')  # The root directory to search for notebooks
OUTPUT_DIR = Path('./build')  # Directory to store the generated blog posts
RESOURCES_DIR = Path('./resources')  # Path to the custom nbconvert template
TEMPLATES_DIR= Path('./resources/site')  # Path to the CSS file
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
    template = 'template_voidptr'

    subprocess.run([
                    "python", "-m", "nbconvert", n_src_file, "--to", "html",
                    f'--TemplateExporter.extra_template_basedirs={template_dir}',
                    f'--template={template}'
                    ])

    output_file = f"{n_src_file.parent / n_src_file.stem}.html"
    shutil.move(output_file , f'{output_dir / n_src_file.stem}.html')

    return output_file


# Set up Jinja2 environment
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

def convert_notebook(n_src_file, output_dir, template_dir):
    """Convert a notebook to HTML using nbconvert."""
    template = 'template_voidptr'

    subprocess.run([
        "python", "-m", "nbconvert", n_src_file, "--to", "html",
        f'--TemplateExporter.extra_template_basedirs={template_dir}',
        f'--template={template}'
    ])

    output_file = f"{n_src_file.parent / n_src_file.stem}.html"
    shutil.move(output_file, f'{output_dir / n_src_file.stem}.html')

    return output_file

def generate_category_page(category, notebooks, output_dir):
    """Generate a category page with links to notebooks using Jinja template."""
    notebook_links = []
    for notebook in notebooks:
        notebook_links.append({
            'title': notebook.stem.replace('_', ' ').title(),
            'url': f"{notebook.stem}.html"
        })
    
    template = env.get_template('category.html')
    category_html = template.render(
        category=str(category),
        notebooks=notebook_links,
        active_page=''  # No active page for category pages
    )
    
    category_page_path = output_dir / f"{category}.html"
    with open(category_page_path, 'w') as f:
        f.write(category_html)

def generate_homepage(notebooks_by_category, output_dir):
    """Generate homepage with featured posts using Jinja template."""
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Prepare featured posts data
    featured_posts = []
    featured_count = 0
    
    for category, notebooks in notebooks_by_category.items():
        category_dir = category if category != Path('.') else ''
        for notebook in notebooks[:2]:  # Limit to 2 notebooks per category
            if featured_count >= 6:  # Limit to 6 featured posts total
                break
                
            featured_posts.append({
                'category': str(category),
                'title': notebook.stem.replace('_', ' ').title(),
                'url': f"{category_dir}/{notebook.stem}.html"
            })
            featured_count += 1
        
        if featured_count >= 6:
            break
    
    # Render homepage
    template = env.get_template('homepage.html')
    index_html = template.render(
        featured_posts=featured_posts,
        active_page='home'
    )
    
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"Site successfully built at {output_dir}/index.html")

def main():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
    
    # Copy static assets
    shutil.copy(CSS_FILE, OUTPUT_DIR / CSS_FILE.name)

    notebooks_by_category = search_notebooks(ROOT_DIR)
    for category, notebooks in notebooks_by_category.items():
        category_output_dir = OUTPUT_DIR / category
        category_output_dir.mkdir(parents=True, exist_ok=True)
        
        for n in notebooks:
            convert_notebook(n, category_output_dir, RESOURCES_DIR)
        
        # Generate category page
        generate_category_page(category, notebooks, category_output_dir)
    
    # Generate homepage
    generate_homepage(notebooks_by_category, OUTPUT_DIR)

if __name__ == "__main__":
    main()