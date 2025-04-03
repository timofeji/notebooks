import os
import shutil

from notebooks import *
from core import *


SAMPLE_PUBLICATIONS = [
    {
        'title': 'AnimBaker',
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


def generate_website(notebooks_by_category, output_dir):
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

    OUTPUT_STYLES_DIR = OUTPUT_DIR / 'styles'
    if not OUTPUT_STYLES_DIR.exists():
        OUTPUT_STYLES_DIR.mkdir(parents=True)

    
    OUTPUT_SCRIPTS_DIR = OUTPUT_DIR / 'scripts'
    if not OUTPUT_SCRIPTS_DIR.exists():
        OUTPUT_SCRIPTS_DIR.mkdir(parents=True)
 
    
    for filename in os.listdir(STYLE_DIR):
        if filename.endswith(".css"): 
            src_path = os.path.join(STYLE_DIR, filename)
            dest_path = os.path.join(OUTPUT_STYLES_DIR, filename)
            shutil.copy2(src_path, dest_path) 

    for filename in os.listdir(SCRIPTS_DIR):
        if filename.endswith(".js"): 
            src_path = os.path.join(SCRIPTS_DIR, filename)
            dest_path = os.path.join(OUTPUT_SCRIPTS_DIR, filename)
            shutil.copy2(src_path, dest_path) 



    notebooks_by_category = search_notebooks(NOTEBOOK_DIR)
    for category, notebooks in notebooks_by_category.items():
        category_output_dir = OUTPUT_DIR / category
        category_output_dir.mkdir(parents=True, exist_ok=True)
        
        for n in notebooks:
            generate_notebook(n, category_output_dir, RESOURCES_DIR)
        
        # Generate category page
        # generate_category_page(category, notebooks, category_output_dir)
    
    # Generate homepage and other pages
    generate_website(notebooks_by_category, OUTPUT_DIR)

if __name__ == "__main__":
    main()