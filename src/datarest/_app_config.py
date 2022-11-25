# Load the central app.yaml configuration file and provide it for use in other
# modules.

import _cfgfile

# config is the main entry point for other modules to read the config
# information. config is an AppConfig model object.
config = _cfgfile.read_app_config()
