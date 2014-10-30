'''
 * Author: Lukasz Jachym
 * Date: 9/27/13
 * Time: 11:46 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''

import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    @property
    def line_num(self):
        return self.reader.line_num

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        try:
            self.writer.writerow([unicode(s).encode("utf-8") for s in row])

        except UnicodeDecodeError as e:
            self.writer.writerow(row)

        except Exception as e:
            print(row)
            raise e

        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class UnicodeDictWriter(csv.DictWriter, object):
    def __init__(self, f, fieldnames, restval="", extrasaction="raise", dialect="excel", *args, **kwds):
        super(UnicodeDictWriter, self).__init__(f, fieldnames, restval=restval, extrasaction=extrasaction, dialect=dialect, *args, **kwds)
        self.writer = UnicodeWriter(f, dialect, **kwds)

class UnicodeDictReader(csv.DictReader, object):
    def __init__(self, f, fieldnames = None, restkey = None, restval="", dialect="excel", *args, **kwds):
        super(UnicodeDictReader, self).__init__(f, fieldnames = fieldnames, restkey = restkey, restval=restval, dialect=dialect, *args, **kwds)
        self.reader = UnicodeReader(f, dialect, **kwds)