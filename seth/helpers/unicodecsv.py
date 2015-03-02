# -*- coding: utf-8 -*-
import csv


def _stringify(s, encoding, errors):
    if s is None:
        return ''
    if isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif isinstance(s, (int , float)):
        pass
    elif not isinstance(s, str):
        s = str(s)
    return s


def _stringify_list(l, encoding, errors='strict'):
    try:
        return [_stringify(s, encoding, errors) for s in iter(l)]
    except TypeError, e:
        raise csv.Error(str(e))


def _unicodify(s, encoding):
    if s is None:
        return None
    if isinstance(s, (unicode, int, float)):
        return s
    elif isinstance(s, str):
        return s.decode(encoding)
    return s


class UnicodeReader(object):
    def __init__(self, f, dialect=None, encoding='utf-8', errors='strict',
                 **kwds):
        format_params = ['delimiter', 'doublequote', 'escapechar', 'lineterminator',
                         'quotechar', 'quoting', 'skipinitialspace']
        if dialect is None:
            if not any([kwd_name in format_params for kwd_name in kwds.keys()]):
                dialect = csv.excel
        self.reader = csv.reader(f, dialect, **kwds)
        self.encoding = encoding
        self.encoding_errors = errors

    def next(self):
        row = self.reader.next()
        encoding = self.encoding
        encoding_errors = self.encoding_errors
        float_ = float
        unicode_ = unicode
        return [(value if isinstance(value, float_) else
                 unicode_(value, encoding, encoding_errors)) for value in row]

    def __iter__(self):
        return self

    @property
    def dialect(self):
        return self.reader.dialect

    @property
    def line_num(self):
        return self.reader.line_num


class UnicodeWriter(object):
    def __init__(self, f, dialect=csv.excel, encoding='utf-8', errors='strict',
                 *args, **kwds):
        self.encoding = encoding
        self.writer = csv.writer(f, dialect, *args, **kwds)
        self.encoding_errors = errors

    def writerow(self, row):
        self.writer.writerow(_stringify_list(row, self.encoding, self.encoding_errors))

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    @property
    def dialect(self):
        return self.writer.dialect