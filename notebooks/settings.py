from pathlib import Path
import re
import os

PROJECT_DIR= os.path.dirname(os.path.dirname(__file__))


# Function to extract CSS variables from a CSS file
def load_colors_from_css(css_file):
    with open(css_file, 'r', encoding='utf-8') as f:
        css = f.read()

    # Regex to find CSS variables (match --variable-name: #hexcolor;)
    color_vars = re.findall(r'--([\w-]+):\s*(#[0-9a-fA-F]{6});', css)
    
    # Convert to a dictionary with snake_case keys
    return {name.replace('-', '_'): color for name, color in color_vars}



# Load colors from CSS
colors = load_colors_from_css( os.path.join(PROJECT_DIR , "resources\colors.css"))


import numpy as np
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