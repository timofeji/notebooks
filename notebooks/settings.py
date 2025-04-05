import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# from pathlib import Path
# import re
# import os

# PROJECT_DIR= os.path.dirname(os.path.dirname(__file__))


# # Function to extract CSS variables from a CSS file
# def load_colors_from_css(css_file):
#     with open(css_file, 'r', encoding='utf-8') as f:
#         css = f.read()

#     # Regex to find CSS variables (match --variable-name: #hexcolor;)
#     color_vars = re.findall(r'--([\w-]+):\s*(#[0-9a-fA-F]{6});', css)
    
#     # Convert to a dictionary with snake_case keys
#     return {name.replace('-', '_'): color for name, color in color_vars}



# # Load colors from CSS
# colors = load_colors_from_css( os.path.join(PROJECT_DIR , "resources\styles\colors.css"))




# # Create a custom style dictionary
# earthpunk_plot_style = {
#     # Figure
#     'figure.facecolor': 'none',
#     'figure.edgecolor': colors['accent_dark'],
    
#     # Axes
#     'axes.facecolor': 'none',
#     'axes.edgecolor': colors['accent_gray'],
#     'axes.labelcolor': colors['accent_dark'],
#     'axes.titlecolor': colors['accent_dark'],
#     'axes.grid': True,
#     'axes.spines.top': False,
#     'axes.spines.right': False,
#     'axes.prop_cycle': mpl.cycler(color=[
#         colors['accent_gray'],
#         colors['accent_highlight'],
#         colors['accent_alt'],
#         colors['accent_alt2'],
#         colors['accent_alt'],
#         colors['accent_light_2'],
#         colors['accent_light'],
#     ]),
    
#     # Grid
#     'grid.color': colors['neutral_300'],
#     'grid.linestyle': '--',
#     'grid.linewidth': 0.75,
#     'grid.alpha': 0.7,
    
#     # Text
#     'text.color': colors['text'],
#     'font.family': ['sans-serif'],
#     'font.sans-serif': ['Montserrat', 'Open Sans', 'DejaVu Sans'],
    
#     # Ticks
#     'xtick.color': colors['accent_dark'],
#     'ytick.color': colors['accent_dark'],
#     'xtick.labelcolor': colors['accent_dark'],
#     'ytick.labelcolor': colors['accent_dark'],
    
#     # Legend
#     'legend.frameon': True,
#     'legend.framealpha': 0.9,
#     # 'legend.facecolor': colors['accent_solarized'],
#     'legend.edgecolor': colors['accent_light'],
    
#     # Lines
#     'lines.linewidth': 2.5,
#     'lines.markersize': 7,
    
#     # Scatter
#     'scatter.marker': 'o',
    
#     # Patches
#     'patch.edgecolor': colors['accent_gray'],
#     'patch.facecolor': colors['accent_light_2'],
    
#     # Saving figures
#     'savefig.dpi': 300,
#     'savefig.facecolor': 'none',
#     'savefig.edgecolor': colors['accent_dark'],
# }

# plt.style.use(earthpunk_plot_style)

