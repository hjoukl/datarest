# Load the central app.yaml configuration file and provide it for use in other
# modules.

import attrdict
import yaml


# read configuration
with open('app.yaml', 'rb') as config_file:
    """config is the main entry point for other modules to read the config information
    AttrDict provides mapping objects that allow their elements to be accessed as keys and as attributes
    """
    config = attrdict.AttrDict(yaml.safe_load(config_file))
