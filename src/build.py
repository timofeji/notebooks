import os
import uuid
import time
import shutil
import hashlib
import asyncio

from notebooks import *
from core import *

WATCH_INTERVAL = 1  # seconds
EXTENSIONS_TO_WATCH = ['.py', '.html', '.css', '.js', '.ipynb']
IGNORED_DIRECTORIES = ['./.git', str(OUTPUT_DIR)]

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


def generate_website(nb_by_category, nb_page_settings):
    """Generate homepage with featured posts using Jinja template."""

    # Set page depth for homepage (root level)
    env.set_page_depth(0)
    
    # Prepare featured posts data
    featured_posts = []

    for nb_settings in nb_page_settings:
        featured_posts.append(nb_settings)
    # Render homepage
    template = env.get_template('homepage.html')
    index_html = template.render(
        post_settings = featured_posts,
        active_page='home'
    )
    
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Generate other main pages
    generate_about_page(OUTPUT_DIR)
    # generate_publications_page(output_dir)
    # generate_portfolio_page(output_dir)
    
    print(f"Site successfully built at {OUTPUT_DIR}/index.html")

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


def run_build(files_to_build=None):
    print(files_to_build)


    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    OUTPUT_STYLES_DIR = OUTPUT_DIR / 'styles'
    if not OUTPUT_STYLES_DIR.exists():
        OUTPUT_STYLES_DIR.mkdir(parents=True)

    OUTPUT_STATIC_DIR = OUTPUT_DIR / 'static'
    if not OUTPUT_STATIC_DIR.exists():
        OUTPUT_STATIC_DIR.mkdir(parents=True)

    OUTPUT_SCRIPTS_DIR = OUTPUT_DIR / 'scripts'
    if not OUTPUT_SCRIPTS_DIR.exists():
        OUTPUT_SCRIPTS_DIR.mkdir(parents=True)

    for root, _, files in os.walk(RESOURCES_DIR):
        for filename  in files:
            src_path = Path(root) / filename
            if filename.endswith(".css"): 
                dest_path = os.path.join(OUTPUT_STYLES_DIR, filename)
                shutil.copy2(src_path, dest_path) 
            elif filename.endswith(".js"): 
                dest_path = os.path.join(OUTPUT_SCRIPTS_DIR, filename)
                shutil.copy2(src_path, dest_path) 
            elif filename.endswith(( ".svg", ".png", ".jpg" )) :
                dest_path = os.path.join(OUTPUT_STATIC_DIR, filename)
                shutil.copy2(src_path, dest_path) 

    
    nb_sources = search_notebooks(NOTEBOOK_DIR)

    nb_page_settings = []
    for nb_path, nb_file in nb_sources.items():
        for nb_file in nb_file:
            _, settings = generate_notebook_page(nb_file)

            img_id = str(uuid.uuid4())
            src_path = os.path.join(NOTEBOOK_DIR,nb_path, Path(settings['image']))
            dest_path = os.path.join(OUTPUT_STATIC_DIR, img_id)
            shutil.copy2(src_path, dest_path) 
            settings['image'] = f'static/{img_id}'
            nb_page_settings.append(settings)

    # Generate homepage and other pages
    generate_website(nb_sources, nb_page_settings)

def get_file_hashes(directory='.', extensions=None):
    """Get hash of all files in directory with specified extensions"""
    file_hashes = {}
    for root, _, files in os.walk(directory):
        # Skip ignored directories
        if any(ignored_dir in root for ignored_dir in IGNORED_DIRECTORIES):
            continue
            
        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            # Filter by extension if specified
            if extensions and not any(file.endswith(ext) for ext in extensions):
                continue
                
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    file_hashes[filepath] = file_hash
            except (IOError, PermissionError):
                continue
    return file_hashes

async def watch_for_changes():
    """Watch for file changes and run build.py when detected"""
    # Initial build
    
    print(f"🔍 Watching for changes to files with extensions: {', '.join(EXTENSIONS_TO_WATCH)}")
    print(f"⏱️ Checking every {WATCH_INTERVAL} second(s)")
    print("📝 Press Ctrl+C to stop")
    
    # Get initial file hashes
    last_file_hashes = get_file_hashes(extensions=EXTENSIONS_TO_WATCH)

   
    
    try:
        while True:
            time.sleep(WATCH_INTERVAL)
            current_file_hashes = get_file_hashes(extensions=EXTENSIONS_TO_WATCH)
            
            # Check for changes
            if current_file_hashes != last_file_hashes:
                # Find changed files
                changed_files = []
                for file, hash_value in current_file_hashes.items():
                    if file not in last_file_hashes or last_file_hashes[file] != hash_value:
                        changed_files.append(file)
                
                for file in last_file_hashes:
                    if file not in current_file_hashes:
                        changed_files.append(f"{file} (deleted)")
                
                # Check if any special directories were modified
                special_dirs_changed = []
                # for file in changed_files:
                #     for special_dir in SPECIAL_WATCH_DIRECTORIES:
                #         if file.startswith(special_dir):
                #             if special_dir not in special_dirs_changed:
                #                 special_dirs_changed.append(special_dir)
                
                # Print changed files (limit to 5 to avoid clutter)
                if changed_files:
                    print(f"🔄 Changes detected in {len(changed_files)} file(s):")
                    for file in changed_files[:5]:
                        print(f"  - {file}")
                    if len(changed_files) > 5:
                        print(f"  - ...and {len(changed_files) - 5} more")
                    
                    if special_dirs_changed:
                        print(f"🔔 Special directories changed: {', '.join(special_dirs_changed)}")
                    
                    # Run build with configuration
                    run_build(special_dirs_changed)
                    
                # Update hashes
                last_file_hashes = current_file_hashes
                await notify_clients()

    except KeyboardInterrupt:
        print("\n👋 File watcher stopped")

clients = set()  # Store connected WebSocket clients
async def websocket_handler(websocket, path):
    """ Handle WebSocket connections """
    print("Client connected")
    clients.add(websocket)
    try:
        async for message in websocket:
            pass  # Keep connection open
    finally:
        clients.remove(websocket)
        print("Client disconnected")

async def notify_clients(file_types=None):
    """ Notify all connected clients to reload specific file types """

    print(clients)
    for client in clients:
        client.send("reload")

import websockets
async def start_watcher():
    """ Start the file watcher and WebSocket server properly """
    # Create and start the WebSocket server first
    # server = await websockets.serve(websocket_handler, "localhost", 8765)
    print("WebSocket server running on ws://localhost:8765")

    # Start the file checking loop in the background
    asyncio.create_task(watch_for_changes())
    # loop = asyncio.get_event_loop()
    # loop.run_forever()  # Keep the loop alive

    

def main(cfg):
    run_build(cfg)
    if cfg.watch:
        asyncio.run(start_watcher())
        
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action=argparse.BooleanOptionalAction, help='watch for changes in files')
    parser.set_defaults()
    cfg = parser.parse_args()
    main(cfg)