# Some cure for YAML hassles
import yaml


def str_representer(dumper, data):
    """Dump data as str(data) in YAML.
    """
    return dumper.represent_str(str(data))


def dump_as_str(cls):
    """Class decorator, register cls to YAML-dump objects as str(obj).
    """
    # The PyYAML docs really could be better...
    #yaml.add_representer(cls, str_representer)
    yaml.add_representer(cls, str_representer, Dumper=yaml.SafeDumper)
    return cls


def dump_decimal_as_str():
    import decimal
    dump_as_str(decimal.Decimal)


def set_selective_str_blockstyle(Dumper, block_style='|'):
    """Add a str representer to `Dumper` that uses string (block) style
    `block_style` for lines containing \n characters.

    Note: This won't work if the string data contains special escapes. It's
    also very sensitive to non-empty whitespace-only lines, e.g. if the data
    contains lines like ' $' ($ denoting the line end). In these cases double
    quotes are enforced regardless. 
    """ 
    def selective_str_representer(dumper, data):
        style = None
        if '\n' in data:
            print(dumper, data)
            style = block_style
        return dumper.represent_scalar(
            u'tag:yaml.org,2002:str', data, style=style
            )

    yaml.add_representer(
        str, selective_str_representer, Dumper=Dumper)


