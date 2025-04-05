import base64
import io
import json
from nbconvert.preprocessors import Preprocessor
import matplotlib.pyplot as plt
import numpy as np
import plotly
import plotly.graph_objs as go
from IPython.display import display, HTML


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
    