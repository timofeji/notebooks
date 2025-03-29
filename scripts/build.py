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
        <title>Timofej Jermolaev</title>
        <meta name="description" content="Personal website of Timofej Jermolaev, showcasing research, publications, and portfolio projects.">
        <link rel="stylesheet" href="styles.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script src="script.js" defer></script>
    </head>
    <body>
        <header>
            <div class="container">
                <h1>Timofej Jermolaev</h1>
                <nav>
                    <ul>
                        <li><a href="index.html" class="active">Home</a></li>
                        <li><a href="publications.html">Publications</a></li>
                        <li><a href="portfolio.html">Portfolio</a></li>
                        <li><a href="about.html">About</a></li>
                    </ul>
                </nav>
            </div>
        </header>



        <main class="container">
            <section class="latest-posts">
                <h2>Latest Work</h2>
                <div class="post-grid">
    '''

    # Add featured posts
    featured_count = 0
    for category, notebooks in notebooks_by_category.items():
        category_dir = category if category != Path('.') else ''
        for notebook in notebooks[:2]:  # Limit to 2 notebooks per category
            if featured_count >= 6:  # Limit to 6 featured posts total
                break
                
            html_content += f'''
                    <div class="post-card">
                        <div class="post-card-content">
                            <span class="category-tag">{category}</span>
                            <h3><a href="{category_dir}/{notebook.stem}.html">{notebook.stem.replace('_', ' ').title()}</a></h3>
                            <p class="post-excerpt">Explore this analysis and discover insights...</p>
                            <a href="{category_dir}/{notebook.stem}.html" class="read-more">Read More</a>
                        </div>
                    </div>'''
            featured_count += 1
        
        if featured_count >= 6:
            break


    # Add categories
    for category in notebooks_by_category.keys():
        category_name = str(category) if category != Path('.') else "General"
        cat_str = str(category) if category != Path('.') else "index"
        html_content += f'''
                    <div class="category-card">
                        <h3>{category_name.replace('_', ' ').title()}</h3>
                        <p>{len(notebooks_by_category[category])} projects</p>
                        <a href="{cat_str}.html" class="btn btn-outline">Explore</a>
                    </div>'''

    # Footer
    html_content += '''
                </div>
            </section>
        </main>

        <footer>
            <div class="container">
                <p>&copy; 2025 Timofej Jermolaev | <a href="#">Contact</a></p>
                <div class="social-links">
                    <a href="#" aria-label="GitHub"><i class="fa-brands fa-github"></i></a>
                    <a href="#" aria-label="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
                    <a href="#" aria-label="Twitter"><i class="fa-brands fa-twitter"></i></a>
                </div>
            </div>
        </footer>
    </body>
    </html>'''

    # Write the final HTML file to the output directory
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Create About page
    create_about_page(output_dir)
    
    # Create Publications page
    create_publications_page(output_dir)
    
    # Create Portfolio page
    create_portfolio_page(output_dir)
    
    print(f"Site successfully built at {output_dir}/index.html")

def create_about_page(output_dir):
    """Create an About page."""
    about_content = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>About - Timofej Jermolaev</title>
        <link rel="stylesheet" href="styles.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script src="script.js" defer></script>
    </head>
    <body>
        <header>
            <div class="container">
                <h1>Timofej Jermolaev</h1>
                <nav>
                    <ul>
                        <li><a href="index.html">Home</a></li>
                        <li><a href="publications.html">Publications</a></li>
                        <li><a href="portfolio.html">Portfolio</a></li>
                        <li><a href="about.html" class="active">About</a></li>
                    </ul>
                </nav>
            </div>
        </header>

        <section class="hero">
            <div class="container">
                <div class="hero-content">
                    <h2>Gamedev & Kinematics Researcher</h2>
                    <p>Exploring the frontiers of machine learning and data analysis</p>
                    <div class="hero-buttons">
                        <a href="portfolio.html" class="btn btn-primary">View Portfolio</a>
                        <a href="about.html" class="btn btn-secondary">About Me</a>
                    </div>
                </div>
            </div>
        </section>

        <main class="container">
            <section class="about-section">
                <div class="about-grid">
                    <div class="about-image">
                        <img src="/api/placeholder/400/500" alt="Timofej Jermolaev">
                    </div>
                    <div class="about-content">
                        <h2>About Me</h2>
                        <p>I am a data scientist and researcher specializing in machine learning, statistical analysis, and data visualization. With over 5 years of experience in the field, I've worked on projects ranging from predictive modeling to natural language processing.</p>
                        
                        <h3>Education</h3>
                        <ul class="timeline">
                            <li>
                                <div class="timeline-content">
                                    <h4>PhD in Computer Science</h4>
                                    <p>Stanford University, 2018-2022</p>
                                </div>
                            </li>
                            <li>
                                <div class="timeline-content">
                                    <h4>MSc in Data Science</h4>
                                    <p>MIT, 2016-2018</p>
                                </div>
                            </li>
                            <li>
                                <div class="timeline-content">
                                    <h4>BSc in Mathematics</h4>
                                    <p>University of Cambridge, 2012-2016</p>
                                </div>
                            </li>
                        </ul>
                        
                        <h3>Skills</h3>
                        <div class="skills-container">
                            <span class="skill-tag">Python</span>
                            <span class="skill-tag">TensorFlow</span>
                            <span class="skill-tag">PyTorch</span>
                            <span class="skill-tag">SQL</span>
                            <span class="skill-tag">R</span>
                            <span class="skill-tag">Machine Learning</span>
                            <span class="skill-tag">Deep Learning</span>
                            <span class="skill-tag">NLP</span>
                            <span class="skill-tag">Data Visualization</span>
                        </div>
                        
                        <h3>Contact</h3>
                        <p>Feel free to reach out for collaborations or inquiries:</p>
                        <p><strong>Email:</strong> timofej@example.com</p>
                        <div class="social-icons">
                            <a href="#" aria-label="GitHub"><i class="fa-brands fa-github"></i></a>
                            <a href="#" aria-label="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
                            <a href="#" aria-label="Twitter"><i class="fa-brands fa-twitter"></i></a>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <footer>
            <div class="container">
                <p>&copy; 2025 Timofej Jermolaev | <a href="#">Contact</a></p>
                <div class="social-links">
                    <a href="#" aria-label="GitHub"><i class="fa-brands fa-github"></i></a>
                    <a href="#" aria-label="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
                    <a href="#" aria-label="Twitter"><i class="fa-brands fa-twitter"></i></a>
                </div>
            </div>
        </footer>
    </body>
    </html>'''
    
    with open(os.path.join(output_dir, 'about.html'), 'w', encoding='utf-8') as f:
        f.write(about_content)

def create_publications_page(output_dir):
    """Create a Publications page."""
    publications_content = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Publications - Timofej Jermolaev</title>
        <link rel="stylesheet" href="styles.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script src="script.js" defer></script>
    </head>
    <body>
        <header>
            <div class="container">
                <h1>Timofej Jermolaev</h1>
                <nav>
                    <ul>
                        <li><a href="index.html">Home</a></li>
                        <li><a href="publications.html" class="active">Publications</a></li>
                        <li><a href="portfolio.html">Portfolio</a></li>
                        <li><a href="about.html">About</a></li>
                    </ul>
                </nav>
            </div>
        </header>

        <main class="container">
            <section class="publications-section">
                <h2>Academic Publications</h2>
                <div class="publications-list">
                    <div class="publication-card">
                        <div class="publication-meta">
                            <span class="publication-year">2024</span>
                            <span class="publication-journal">Nature Machine Intelligence</span>
                        </div>
                        <h3>Improving Generalization in Large Language Models Through Multitask Learning</h3>
                        <p class="publication-authors">Jermolaev, T., Smith, J., & Johnson, A.</p>
                        <div class="publication-links">
                            <a href="#" class="btn btn-sm">PDF</a>
                            <a href="#" class="btn btn-sm">DOI</a>
                            <a href="#" class="btn btn-sm">Code</a>
                        </div>
                    </div>
                    
                    <div class="publication-card">
                        <div class="publication-meta">
                            <span class="publication-year">2023</span>
                            <span class="publication-journal">ICML</span>
                        </div>
                        <h3>Neural Network Pruning Techniques for Efficient On-Device Inference</h3>
                        <p class="publication-authors">Jermolaev, T., & Anderson, K.</p>
                        <div class="publication-links">
                            <a href="#" class="btn btn-sm">PDF</a>
                            <a href="#" class="btn btn-sm">DOI</a>
                            <a href="#" class="btn btn-sm">Code</a>
                        </div>
                    </div>
                    
                    <div class="publication-card">
                        <div class="publication-meta">
                            <span class="publication-year">2022</span>
                            <span class="publication-journal">NeurIPS</span>
                        </div>
                        <h3>Transformer Architectures for Time Series Forecasting: A Comparative Analysis</h3>
                        <p class="publication-authors">Jermolaev, T., Williams, S., & Chen, L.</p>
                        <div class="publication-links">
                            <a href="#" class="btn btn-sm">PDF</a>
                            <a href="#" class="btn btn-sm">DOI</a>
                            <a href="#" class="btn btn-sm">Code</a>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <footer>
            <div class="container">
                <p>&copy; 2025 Timofej Jermolaev | <a href="#">Contact</a></p>
                <div class="social-links">
                    <a href="#" aria-label="GitHub"><i class="fa-brands fa-github"></i></a>
                    <a href="#" aria-label="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
                    <a href="#" aria-label="Twitter"><i class="fa-brands fa-twitter"></i></a>
                </div>
            </div>
        </footer>
    </body>
    </html>'''
    
    with open(os.path.join(output_dir, 'publications.html'), 'w', encoding='utf-8') as f:
        f.write(publications_content)

def create_portfolio_page(output_dir):
    """Create a Portfolio page."""
    portfolio_content = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Portfolio - Timofej Jermolaev</title>
        <link rel="stylesheet" href="styles.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script src="script.js" defer></script>
    </head>
    <body>
        <header>
            <div class="container">
                <h1>Timofej Jermolaev</h1>
                <nav>
                    <ul>
                        <li><a href="index.html">Home</a></li>
                        <li><a href="publications.html">Publications</a></li>
                        <li><a href="portfolio.html" class="active">Portfolio</a></li>
                        <li><a href="about.html">About</a></li>
                    </ul>
                </nav>
            </div>
        </header>

        <main class="container">
            <section class="portfolio-section">
                <h2>Project Portfolio</h2>
                <div class="portfolio-filters">
                    <button class="portfolio-filter active" data-filter="all">All</button>
                    <button class="portfolio-filter" data-filter="machine-learning">Machine Learning</button>
                    <button class="portfolio-filter" data-filter="data-analysis">Data Analysis</button>
                    <button class="portfolio-filter" data-filter="visualization">Visualization</button>
                </div>
                
                <div class="portfolio-grid">
                    <div class="portfolio-card" data-category="machine-learning">
                        <div class="portfolio-image">
                            <img src="/api/placeholder/400/300" alt="Neural Network Project">
                        </div>
                        <div class="portfolio-content">
                            <h3>Deep Learning for Image Recognition</h3>
                            <p>Implementation of a convolutional neural network for image classification tasks.</p>
                            <div class="portfolio-tags">
                                <span class="tag">PyTorch</span>
                                <span class="tag">CNN</span>
                                <span class="tag">Computer Vision</span>
                            </div>
                            <a href="#" class="btn btn-primary">View Project</a>
                        </div>
                    </div>
                    
                    <div class="portfolio-card" data-category="data-analysis">
                        <div class="portfolio-image">
                            <img src="/api/placeholder/400/300" alt="Data Analysis Project">
                        </div>
                        <div class="portfolio-content">
                            <h3>Financial Market Prediction</h3>
                            <p>Time series analysis of financial markets using ARIMA and LSTM models.</p>
                            <div class="portfolio-tags">
                                <span class="tag">Time Series</span>
                                <span class="tag">LSTM</span>
                                <span class="tag">Finance</span>
                            </div>
                            <a href="#" class="btn btn-primary">View Project</a>
                        </div>
                    </div>
                    
                    <div class="portfolio-card" data-category="visualization">
                        <div class="portfolio-image">
                            <img src="/api/placeholder/400/300" alt="Data Visualization Project">
                        </div>
                        <div class="portfolio-content">
                            <h3>Interactive Climate Data Dashboard</h3>
                            <p>Interactive dashboard for exploring global climate data patterns.</p>
                            <div class="portfolio-tags">
                                <span class="tag">D3.js</span>
                                <span class="tag">Plotly</span>
                                <span class="tag">Interactive</span>
                            </div>
                            <a href="#" class="btn btn-primary">View Project</a>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <footer>
            <div class="container">
                <p>&copy; 2025 Timofej Jermolaev | <a href="#">Contact</a></p>
                <div class="social-links">
                    <a href="#" aria-label="GitHub"><i class="fa-brands fa-github"></i></a>
                    <a href="#" aria-label="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
                    <a href="#" aria-label="Twitter"><i class="fa-brands fa-twitter"></i></a>
                </div>
            </div>
        </footer>
    </body>
    </html>'''
    
    with open(os.path.join(output_dir, 'portfolio.html'), 'w', encoding='utf-8') as f:
        f.write(portfolio_content)


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
        
    
   
    generate_homepage(notebooks_by_category, OUTPUT_DIR)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--config', type=str, default="default", help='configuration for setup')
    # parser.set_defaults()
    # cfg = parser.parse_args()

    # if cfg.watch:
    main()
