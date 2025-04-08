import jinja2
from pathlib import Path

OUTPUT_DIR = Path('./build')  # Directory to store the generated blog posts
NOTEBOOK_DIR = Path('./notebooks')  # The root directory to search for notebooks
RESOURCES_DIR = Path('./resources')  # Path to the custom nbconvert template
TEMPLATES_DIR= Path('./resources/templates')  # Path to the CSS file
STYLE_DIR = Path('./resources/styles')  # Path to the CSS file
SCRIPTS_DIR = Path('./resources/scripts')  # Path to the CSS file
OUTPUT_IMG_DIR = OUTPUT_DIR / 'static/img'

# Custom Jinja2 environment with path utilities
class PathAwareEnvironment(jinja2.Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_page_depth = 0
        
    def set_page_depth(self, depth):
        self.current_page_depth = depth
        
    def get_template(self, name, *args, **kwargs):
        template = super().get_template(name, *args, **kwargs)
        template.globals['url_static'] = self.url_static
        template.globals['url_page'] = self.url_page
        return template
        
    def url_static(self, path):
        prefix = '../' * self.current_page_depth
        return f"{prefix}{path}"
        
    def url_page(self, path):
        prefix = '../' * self.current_page_depth
        return f"{prefix}{path}"

# Set up Jinja2 environment
env = PathAwareEnvironment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)



# class HTMLCard:
#     def __init__(self, image_path, title, description):
#         self.image_path = image_path
#         self.title = title
#         self.description = description
    
#     def _repr_html_(self):
#         # Generates HTML with inline styling for simplicity
#         return f"""
#         <div style="
#             border: 1px solid #ddd;
#             border-radius: 8px;
#             padding: 15px;
#             margin: 10px;
#             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#             max-width: 300px;
#         ">
#             <img src="{self.image_path}" 
#                  style="
#                     width: 100%;
#                     height: auto;
#                     border-radius: 4px;
#                  ">
#             <h3 style="margin: 10px 0; color: #333;">{self.title}</h3>
#             <p style="color: #666; font-size: 0.9em;">{self.description}</p>
#         </div>
#         """
