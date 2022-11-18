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
    yaml.add_representer(cls, str_representer)
    yaml.add_representer(cls, str_representer, Dumper=yaml.SafeDumper)
    return cls


def dump_decimal_as_str():
    import decimal
    dump_as_str(decimal.Decimal)
