import os

import toml

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.toml')
config_data = toml.load(config_path)
