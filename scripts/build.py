from collections import defaultdict
import os
import subprocess
import shutil
import jinja2
from pathlib import Path


# Define the solarpunk color palette from CSS variables
colors = {
    'earth_deep': '#2c3b2d',
    'earth_medium': '#3a5a40',
    'earth_light': '#588157',
    'solar_green': '#a3b18a',
    'solar_glow': '#dad7cd',
    'amber_gold': '#e9c46a',
    'leaf_highlight': '#80b192',
    'terracotta': '#bb5a41',
    'sunset_orange': '#e76f51',
    'neutral_100': '#f6f7f4',
    'neutral_300': '#ccd5c4',
    'neutral_800': '#2c3b2d',
}


import matplotlib as mpl
import matplotlib.pyplot as plt


# Create a custom style dictionary
earthpunk_plot_style = {
    # Figure
    'figure.facecolor': colors['neutral_100'],
    'figure.edgecolor': colors['earth_deep'],
    
    # Axes
    'axes.facecolor': colors['neutral_100'],
    'axes.edgecolor': colors['earth_medium'],
    'axes.labelcolor': colors['earth_deep'],
    'axes.titlecolor': colors['earth_deep'],
    'axes.grid': True,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.prop_cycle': mpl.cycler(color=[
        colors['earth_medium'],
        colors['leaf_highlight'],
        colors['sunset_orange'],
        colors['amber_gold'],
        colors['terracotta'],
        colors['solar_green'],
        colors['earth_light'],
    ]),
    
    # Grid
    'grid.color': colors['neutral_300'],
    'grid.linestyle': '--',
    'grid.linewidth': 0.75,
    'grid.alpha': 0.7,
    
    # Text
    'text.color': colors['earth_deep'],
    'font.family': ['sans-serif'],
    'font.sans-serif': ['Montserrat', 'Open Sans', 'DejaVu Sans'],
    
    # Ticks
    'xtick.color': colors['earth_deep'],
    'ytick.color': colors['earth_deep'],
    'xtick.labelcolor': colors['earth_deep'],
    'ytick.labelcolor': colors['earth_deep'],
    
    # Legend
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.facecolor': colors['solar_glow'],
    'legend.edgecolor': colors['earth_light'],
    
    # Lines
    'lines.linewidth': 2.5,
    'lines.markersize': 7,
    
    # Scatter
    'scatter.marker': 'o',
    
    # Patches
    'patch.edgecolor': colors['earth_medium'],
    'patch.facecolor': colors['solar_green'],
    
    # Saving figures
    'savefig.dpi': 300,
    'savefig.facecolor': colors['neutral_100'],
    'savefig.edgecolor': colors['earth_deep'],
}

plt.style.use(earthpunk_plot_style)



ROOT_DIR = Path('./src')  # The root directory to search for notebooks
OUTPUT_DIR = Path('./build')  # Directory to store the generated blog posts
RESOURCES_DIR = Path('./resources')  # Path to the custom nbconvert template
TEMPLATES_DIR= Path('./resources/site')  # Path to the CSS file
CSS_FILE = Path('./resources/styles.css')  # Path to the CSS file

SAMPLE_PUBLICATIONS = [
    {
        'title': 'An Analysis of Machine Learning Techniques for Time Series Prediction',
        'authors': 'Jermolaev, T., Smith, J., & Johnson, A.',
        'venue': 'Journal of Data Science',
        'year': 2024,
        'type': 'journal',
        'pdf_url': '#',
        'doi': '10.1234/abcd',
        'code_url': '#'
    },
    {
        'title': 'Novel Approaches to Natural Language Processing',
        'authors': 'Jermolaev, T. & Wilson, B.',
        'venue': 'International Conference on Machine Learning',
        'year': 2023,
        'type': 'conference',
        'pdf_url': '#',
        'code_url': '#'
    }
]

SAMPLE_PROJECTS = [
    {
        'title': 'Montage Graph',
        'description': 'A graph base editor extension for Unreal Engine, aimed at helping authoring montage based combo attacks',
        'technologies': ['C++', 'Unreal Engine', 'Skeletal Animation'],
        'demo_url': '#',
        'code_url': '#'
    },
    {
        'title': 'AnimBaker',
        'description': 'A machine learning model for predicting future values in time series data.',
        'technologies': ['C++', 'Unreal Engine', 'Skeletal Animation'],
        'code_url': '#'
    }
]

# Custom Jinja2 environment with path utilities
class PathAwareEnvironment(jinja2.Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_page_depth = 0
        
    def set_page_depth(self, depth):
        self.current_page_depth = depth
        
    def get_template(self, name, *args, **kwargs):
        template = super().get_template(name, *args, **kwargs)
        template.globals['url_for_static'] = self.url_for_static
        template.globals['url_for_page'] = self.url_for_page
        return template
        
    def url_for_static(self, path):
        prefix = '../' * self.current_page_depth
        return f"{prefix}{path}"
        
    def url_for_page(self, path):
        prefix = '../' * self.current_page_depth
        return f"{prefix}{path}"

# Set up Jinja2 environment
env = PathAwareEnvironment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

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
    shutil.move(output_file, f'{output_dir / n_src_file.stem}.html')

    return output_file

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

def generate_homepage(notebooks_by_category, output_dir):
    """Generate homepage with featured posts using Jinja template."""
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Set page depth for homepage (root level)
    env.set_page_depth(0)
    
    # Prepare featured posts data
    featured_posts = []
    featured_count = 0
    
    for category, notebooks in notebooks_by_category.items():
        category_dir = category if category != Path('.') else ''
        for notebook in notebooks[:2]:  # Limit to 2 notebooks per category
            if featured_count >= 6:  # Limit to 6 featured posts total
                break
                
            featured_posts.append({
                'category': str(category) if str(category) != '.' else 'Main',
                'title': notebook.stem.replace('_', ' ').title(),
                'url': f"{category_dir}/{notebook.stem}.html" if category_dir else f"{notebook.stem}.html"
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
    
    # Generate other main pages
    generate_about_page(output_dir)
    generate_publications_page(output_dir)
    generate_portfolio_page(output_dir)
    
    print(f"Site successfully built at {output_dir}/index.html")

def generate_about_page(output_dir):
    """Generate the about page using Jinja template."""
    env.set_page_depth(0)  # Root level page
    template = env.get_template('about.html')
    about_html = template.render(active_page='about')
    
    with open(os.path.join(output_dir, 'about.html'), 'w', encoding='utf-8') as f:
        f.write(about_html)

def generate_publications_page(output_dir):
    """Generate the publications page using Jinja template."""
    env.set_page_depth(0)  # Root level page
    template = env.get_template('publications.html')
    publications_html = template.render(
        active_page='publications',
        publications=SAMPLE_PUBLICATIONS
    )
    
    with open(os.path.join(output_dir, 'publications.html'), 'w', encoding='utf-8') as f:
        f.write(publications_html)

def generate_portfolio_page(output_dir):
    """Generate the portfolio page using Jinja template."""
    env.set_page_depth(0)  # Root level page
    template = env.get_template('portfolio.html')
    portfolio_html = template.render(
        active_page='portfolio',
        projects=SAMPLE_PROJECTS
    )
    
    with open(os.path.join(output_dir, 'portfolio.html'), 'w', encoding='utf-8') as f:
        f.write(portfolio_html)

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
    
    # Generate homepage and other pages
    generate_homepage(notebooks_by_category, OUTPUT_DIR)

if __name__ == "__main__":
    main()