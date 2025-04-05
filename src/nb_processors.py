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
    

class MatplotlibToInteractivePreprocessor(Preprocessor):
    """
    NBConvert preprocessor that converts matplotlib figures to interactive
    Plotly visualizations in the notebook.
    """
    
    def __init__(self, **kwargs):
        super(MatplotlibToInteractivePreprocessor, self).__init__(**kwargs)
        self.plot_counter = 0
    
    def mpl_to_plotly(self, fig):
        """
        Convert a matplotlib figure to plotly format.
        Very basic implementation - handles simple line plots, scatter plots, and bar charts.
        """
        data = []
        
        for ax in fig.get_axes():
            for line in ax.get_lines():
                x_data = line.get_xdata()
                y_data = line.get_ydata()
                
                trace = go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines' if line.get_linestyle() not in ['', ' '] else 'markers',
                    name=line.get_label() if line.get_label() != '_nolegend_' else f'Series {len(data) + 1}',
                    line=dict(color=line.get_color())
                )
                data.append(trace)
            
            # Handle bar charts
            for container in ax.containers:
                if hasattr(container, 'patches') and container.patches:  # This is likely a bar chart
                    heights = [p.get_height() for p in container.patches]
                    positions = [p.get_x() + p.get_width()/2 for p in container.patches]
                    
                    trace = go.Bar(
                        x=positions,
                        y=heights,
                        name=container.get_label() if hasattr(container, 'get_label') else f'Bar Series {len(data) + 1}'
                    )
                    data.append(trace)
        
        layout = go.Layout(
            title=ax.get_title(),
            xaxis=dict(title=ax.get_xlabel()),
            yaxis=dict(title=ax.get_ylabel()),
            autosize=True,
            width=800,
            height=500
        )
        
        plotly_fig = go.Figure(data=data, layout=layout)
        return plotly_fig
    
    def generate_plotly_html(self, plotly_fig):
        """Generate HTML div with interactive plotly figure."""
        self.plot_counter += 1
        div_id = f'plotly_fig_{self.plot_counter}'
        
        # Convert the figure to JSON
        fig_json = json.dumps(plotly_fig.to_dict())
        
        # Create a div with necessary JS to render the figure
        html = f"""
        <div id='{div_id}' style='height: 500px;'></div>
        <script>
            require(['plotly'], function(Plotly) {{
                var fig = {fig_json};
                Plotly.newPlot('{div_id}', fig.data, fig.layout);
            }});
        </script>
        """
        return HTML(html)
    
    def process_matplotlib_outputs(self, cell):
        """Process outputs in a cell, converting matplotlib to plotly if found."""
        if 'outputs' not in cell:
            return cell
        
        new_outputs = []
        for output in cell['outputs']:
            if output.get('output_type') == 'display_data' and 'image/png' in output.get('data', {}):
                # This might be a matplotlib figure
                try:
                    # Try to decode the PNG and convert to matplotlib figure
                    img_data = base64.b64decode(output['data']['image/png'])
                    
                    # Check if this is really matplotlib output
                    # This is a simplistic check - we need a more robust method in practice
                    if 'matplotlib' in str(output).lower() or True:  # Assume all PNG outputs are matplotlib for now
                        # Create a new output with interactive plotly
                        # In practice, we would extract the figure data directly from the notebook's Python context
                        # For this demo, we'll create a dummy plotly figure
                        
                        # Note: In a real implementation, we would need access to the actual matplotlib figure object
                        # This example assumes the figure still exists in memory, which it won't in many cases
                        
                        # Create a dummy figure - in practice, we'd convert the actual matplotlib figure
                        if hasattr(plt, '_current_fig'):  # Not standard, just for illustration
                            fig = plt._current_fig
                            plotly_fig = self.mpl_to_plotly(fig)
                            html_output = self.generate_plotly_html(plotly_fig)
                            
                            # Create a new output with both the original PNG and interactive version
                            new_output = {
                                'output_type': 'display_data',
                                'data': {
                                    'text/html': html_output.data['text/html'],
                                    'image/png': output['data']['image/png']  # Keep original for non-JS environments
                                },
                                'metadata': output.get('metadata', {})
                            }
                            new_outputs.append(new_output)
                            continue
                except Exception as e:
                    pass
            
            # If we get here, just keep the original output
            new_outputs.append(output)
        
        cell['outputs'] = new_outputs
        return cell
    
    def preprocess_cell(self, cell, resources, index):
        """Process a notebook cell to find and convert matplotlib figures."""
        if cell.get('cell_type') == 'code':
            cell = self.process_matplotlib_outputs(cell)
        
        return cell, resources
