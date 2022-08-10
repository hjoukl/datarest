# Load the central app.yaml configuration file and provide it for use in other
# modules.

from . import _cfgfile

# config is the main entry point for other modules to read the config
# information. config is an AttrDict mapping object that allows elements to be
# accessed both as keys and as attributes
config = _cfgfile.read_app_config()
