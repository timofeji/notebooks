import base64
from nbconvert.preprocessors import Preprocessor
import matplotlib.pyplot as plt
import numpy as np


class PostSettingsPreprocessor(Preprocessor):
    """
    A preprocessor that creates parses settings from a 'POST_SETTINGS' dict.
    """
    def preprocess_cell(self, cell, resources, index):
        """
        Process a single cell and return the modified cell and resources dictionary.
        """
        # We only want to process the first code cell
        if index == 0 and cell.cell_type == 'code':
            # Check if the cell contains SETTINGS
            if 'POST_SETTINGS' in cell.source:
                try:
                    # Extract the SETTINGS dictionary from the code
                    cell_lines = cell.source.strip().split('\n')
                    settings_str = ''
                    started = False
                    
                    for line in cell_lines:
                        if line.strip().startswith('POST_SETTINGS'):
                            started = True
                            settings_str += line.split('=', 1)[1].strip()
                        elif started and not line.strip().endswith('}'):
                            settings_str += line.strip()
                        elif started:
                            settings_str += line.strip()
                            break

                    
                    # Safely evaluate the settings dictionary
                    settings = eval(settings_str)
                    resources['post_settings'] = settings
                    
                except Exception as e:
                    print(f"Error processing POST_SETTINGS: {e}")
        
        return cell, resources


import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse

from nbconvert.preprocessors import Preprocessor

class ImageCopyPreprocessor(Preprocessor):
    """
    A preprocessor that finds all image references in markdown cells and
    copies the referenced images to a specified static directory.
    """
    
    def __init__(self, static_dir=None, **kwargs):
        """
        Initialize the preprocessor.
        
        Parameters:
        -----------
        static_dir : str
            Path to the directory where images should be copied.
            If None, the environment variable STATIC_DIR will be used.
        """
        super().__init__(**kwargs)
        self.static_dir = static_dir or os.environ.get('STATIC_DIR', 'static')
        # Create the static directory if it doesn't exist
        os.makedirs(self.static_dir, exist_ok=True)
        self.image_count = 0
    
    def _extract_image_paths(self, cell_text):
        """
        Extract image paths from markdown cell text.
        
        Returns a list of file paths.
        """
        # Match markdown image syntax: ![alt text](path/to/image.png)
        md_pattern = r'!\[.*?\]\(([^)]+)\)'
        
        # Match HTML image syntax: <img src="path/to/image.png" ... />
        html_pattern = r'<img\s+[^>]*src=["\'](.*?)["\'][^>]*>'
        
        image_paths = []
        
        # Find all markdown image references
        for match in re.finditer(md_pattern, cell_text):
            path = match.group(1)
            # Remove query parameters if present
            path = path.split('?')[0].split('#')[0]
            image_paths.append(path)
        
        # Find all HTML image references
        for match in re.finditer(html_pattern, cell_text):
            path = match.group(1)
            # Remove query parameters if present
            path = path.split('?')[0].split('#')[0]
            image_paths.append(path)
        
        return image_paths
    
    def _copy_image(self, image_path, notebook_dir=None):
        
        print(image_path)
        # Parse the image path
        parsed_path = urlparse(unquote(image_path))
        
        # Skip images with remote URLs
        if parsed_path.scheme in ('http', 'https', 'ftp'):
            return image_path
            
        # Get the local file path
        if parsed_path.path:
            local_path = parsed_path.path
        else:
            local_path = image_path
            
        # Make the path absolute if it's relative
        if notebook_dir and not os.path.isabs(local_path):
            local_path = os.path.join(notebook_dir, local_path)
            
        # Check if the file exists
        if not os.path.isfile(local_path):
            self.log.warning(f"Image file not found: {local_path}")
            return image_path
            
        # Determine the destination file path
        file_name = os.path.basename(local_path)
        base, ext = os.path.splitext(file_name)
        
        # Ensure unique filenames with a counter
        self.image_count += 1
        unique_name = f"{base}_{self.image_count}{ext}"
        dest_path = os.path.join(self.static_dir, unique_name)
        
        # Copy the file
        shutil.copy2(local_path, dest_path)
        self.log.info(f"Copied image: {local_path} -> {dest_path}")
        
        # Return the new path (relative to the static directory)
        return os.path.join(self.static_dir, unique_name)
    
    def _replace_image_paths(self, cell_text, old_path, new_path):
        # Replace in markdown format
        md_pattern = f'!\\[.*?\\]\\({re.escape(old_path)}([^)]*)\\)'
        md_replacement = f'![\\1]({new_path}\\1)'
        cell_text = re.sub(md_pattern, md_replacement, cell_text)
        
        # Replace in HTML format
        html_pattern = f'<img\\s+([^>]*)src=["\']({re.escape(old_path)})(["\'][^>]*)>'
        html_replacement = f'<img \\1src="{new_path}"\\3>'
        cell_text = re.sub(html_pattern, html_replacement, cell_text)
        
        return cell_text
    
    def preprocess_cell(self, cell, resources, index):
        """
        Preprocess a notebook cell.
        
        Parameters:
        -----------
        cell : dict
            Notebook cell.
        resources : dict
            Resources dict.
        index : int
            Cell index.
            
        Returns:
        --------
        tuple
            Processed cell and resources.
        """
        if cell.cell_type == 'markdown':
            # Get the notebook directory
            notebook_path = resources.get('metadata', {}).get('path', '')
            notebook_dir = os.path.dirname(notebook_path) if notebook_path else None
            
            # Extract image paths from the cell text
            image_paths = self._extract_image_paths(cell.source)
            
            # Copy each image and update the cell text
            for old_path in image_paths:
                new_path = self._copy_image(old_path, notebook_dir)
                
                # img_id = str(uuid.uuid4())
                # src_path = os.path.join(NOTEBOOK_DIR,nb_path, Path(settings['image']))
                # dest_path = os.path.join(OUTPUT_IMG_DIR, img_id)
                # shutil.copy2(src_path, dest_path) 
                # settings['image'] = f'static/{img_id}'

                print(os.path.join(str(notebook_path),str(old_path)))

                if new_path != old_path:
                    cell.source = self._replace_image_paths(cell.source, old_path, new_path)
        
        return cell, resources 