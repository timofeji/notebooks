import jinja2
from pathlib import Path

OUTPUT_DIR = Path('./build')  # Directory to store the generated blog posts
NOTEBOOK_DIR = Path('./notebooks')  # The root directory to search for notebooks
RESOURCES_DIR = Path('./resources')  # Path to the custom nbconvert template
TEMPLATES_DIR= Path('./resources/site')  # Path to the CSS file
CSS_FILE = Path('./resources/styles.css')  # Path to the CSS file

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