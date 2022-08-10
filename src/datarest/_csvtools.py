import collections


class CSVInfo(
        collections.namedtuple(
            'CSVInfo', ['dialect', 'has_header'])
        ):
    pass


def detect_csv_properties(csv_filepath, encoding=None):
    """Return csv dialect and has_header info sniffed from csv file.
    """
    with open(csv_filepath, encoding=encoding) as csv_file:
        # Detect CSV dialect from input csv file
        sniffer = csv.Sniffer()
        sample = csv_file.read(1024)
        dialect = sniffer.sniff(sample)
        has_header = sniffer.has_header(sample)
        return CSVInfo(dialect, has_header) 
