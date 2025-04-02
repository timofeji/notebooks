import jinja2
from pathlib import Path

OUTPUT_DIR = Path('./build')  # Directory to store the generated blog posts
NOTEBOOK_DIR = Path('./notebooks')  # The root directory to search for notebooks
RESOURCES_DIR = Path('./resources')  # Path to the custom nbconvert template
TEMPLATES_DIR= Path('./resources/templates')  # Path to the CSS file
STYLE_DIR = Path('./resources/styles')  # Path to the CSS file
SCRIPTS_DIR = Path('./resources/scripts')  # Path to the CSS file

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


