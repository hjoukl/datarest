import collections
import csv
import logging
import mimetypes

import frictionless

from . import _tableschema
from . import _csvtools


class TableschemaInfo(
        collections.namedtuple(
            'TableschemaInfo', ['tableschema', 'datafile_info'])):
    """A namedtuple containing the tableschema JSON schema and a datafile
    specific info object.
    """


def tableschema_from_csv(csv_filepath, encoding=None, primary_key=()):
    """Return a tableschema object from info gathered from a given CSV file.
    """
    csv_info = _csvtools.detect_csv_properties(csv_filepath, encoding=encoding)
    if not csv_info.has_header:
        raise RuntimeError(f'CSV file {csv_filepath} contains no header row.')
    # retrieve column names from input file
    with open(csv_filepath, encoding=encoding) as csv_file:
        csv_reader = csv.DictReader(csv_file, dialect=csv_info.dialect)
        sample_row = list(next(csv_reader).items())
    primary_key = list(primary_key) if primary_key else sample_row[0][0]
    
    schema = _tableschema.Schema(
        fields=[
            _tableschema.Field(
                name=name, type='string', x_datarest_example=value)
            for name, value in sample_row],
        primaryKey=primary_key
        )
    return TableschemaInfo(tableschema=schema, datafile_info=csv_info)


tableschema_readers = {
    'text/csv': tableschema_from_csv,
    }



def tableschema_from_datafile(datafile, encoding=None, primary_key=()):
    """Return a tableschema object from info gathered from a given supported
    data file.
    """
    mimetype, encoding = mimetypes.guess_type(str(datafile))
    try:
        tableschema_info = tableschema_readers[mimetype](
            datafile, encoding=encoding, primary_key=primary_key)
    except KeyError:
        raise NotImplementedError(
            f'Data file {mimetype} currently not supported.')
    return tableschema_info


def read_data(datafile, tableschema_info=None, encoding=None):
    if tableschema_info is None:
        tableschema_info = tableschema_from_datafile(
            datafile, encoding=encoding)

