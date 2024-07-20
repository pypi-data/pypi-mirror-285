import os
import yaml

def load_settings():
    if not os.path.exists('settings.yaml'):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        default_settings_path = os.path.join(file_dir, 'settings.yaml')
        
        with open(default_settings_path, 'r') as default_file:
            default_content = default_file.read()
        
        with open('settings.yaml', 'w') as file:
            file.write(default_content)

    with open('settings.yaml', 'r') as f:
        return yaml.safe_load(f)

settings = load_settings()

BUILD_PATH = settings['build']['path']
if not os.path.isabs(BUILD_PATH):
    BUILD_PATH = os.path.abspath(os.path.join(os.getcwd(), BUILD_PATH))
# else:
#     # project dir and build
#     BUILD_PATH =  os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), BUILD_PATH))

EXCLUDE_FILES = settings['exclude']['files']
EXCLUDE_DIRS = settings['exclude']['dirs']
EXCLUDE_COPYING_FILES = settings['exclude']['copying_files']
EXCLUDE_COPYING_DIRS = settings['exclude']['copying_dirs']
LOG_DIR = settings['logging']['dir']
LOG_FILENAME = settings['logging']['filename']
CYTHON_LANGUAGE_LEVEL = settings['cython']['language_level']