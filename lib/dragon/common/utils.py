# Copyright (C) 2010-2013 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import time
import shutil
import ntpath
import string
import tempfile
import xmlrpclib
from datetime import datetime

from lib.dragon.common.exceptions import CuckooOperationalError

def create_folders(root=".", folders=[]):
    """Create directories.
    @param root: root path.
    @param folders: folders list to be created.
    @raise CuckooOperationalError: if fails to create folder.
    """
    for folder in folders:
        if os.path.exists(os.path.join(root, folder)):
            continue
        else:
            create_folder(root, folder)

def create_folder(root=".", folder=None):
    """Create directory.
    @param root: root path.
    @param folder: folder name to be created.
    @raise CuckooOperationalError: if fails to create folder.
    """
    if not os.path.exists(os.path.join(root, folder)) and folder:
        try:
            folder_path = os.path.join(root, folder)
            os.makedirs(folder_path)
        except OSError as e:
            raise CuckooOperationalError(f"Unable to create folder: {folder_path}")

def delete_folder(folder):
    """Delete a folder and all its subdirectories.
    @param folder: path to delete.
    @raise CuckooOperationalError: if fails to delete folder.
    """
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
        except OSError as e:
            raise CuckooOperationalError("Unable to delete folder: {0}".format(folder))

def convert_char(c):
    """Escapes characters.
    @param c: dirty char.
    @return: sanitized char.
    """
    return c if c in string.printable else r'\x%02x' % ord(c)

def convert_to_printable(s):
    """Convert char to printable.
    @param s: string.
    @return: sanitized string.
    """
    return ''.join(convert_char(c) for c in s)

def datetime_to_iso(timestamp):
    """Parse a datatime string and returns a datetime in iso format.
    @param timestamp: timestamp string
    @return: ISO datetime
    """  
    return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').isoformat()

def get_filename_from_path(path):
    """Cross-platform filename extraction from path.
    @param path: file path.
    @return: filename.
    """
    dirpath, filename = ntpath.split(path)
    return filename or ntpath.basename(dirpath)

def store_temp_file(filedata, filename):
    """Store a temporary file.
    @param filedata: content of the original file.
    @param filename: name of the original file.
    @return: path to the temporary file.
    """
    filename = get_filename_from_path(filename)

    # reduce length (100 is arbitrary)
    filename = filename[:100]

    tmppath = tempfile.gettempdir()
    targetpath = os.path.join(tmppath, "cuckoo-tmp")
    if not os.path.exists(targetpath):
        os.mkdir(targetpath)

    tmp_dir = tempfile.mkdtemp(prefix="upload_", dir=targetpath)
    tmp_file_path = os.path.join(tmp_dir, filename)
    with open(tmp_file_path, "wb") as tmp_file:
            # if filedata is file object, do chunked copy
        if hasattr(filedata, 'read'):
            while chunk := filedata.read(1024):
                tmp_file.write(chunk)
        else:
            tmp_file.write(filedata)

    return tmp_file_path

# xmlrpc + timeout - still a bit ugly - but at least gets rid of setdefaulttimeout
# inspired by 
# http://stackoverflow.com/questions/372365/set-timeout-for-xmlrpclib-serverproxy
# (although their stuff was messy, this is cleaner)
class TimeoutServer(xmlrpclib.ServerProxy):
    def __init__(self, *args, **kwargs):
        timeout = kwargs.pop('timeout', None)
        kwargs['transport'] = TimeoutTransport(timeout=timeout)
        xmlrpclib.ServerProxy.__init__(self, *args, **kwargs)

    def _set_timeout(self, timeout):
        t = self._ServerProxy__transport
        t.timeout = timeout
        # if we still have a socket we need to update that as well
        if hasattr(t, '_connection') and t._connection[1] and t._connection[1].sock:
            t._connection[1].sock.settimeout(timeout)

class TimeoutTransport(xmlrpclib.Transport):
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop('timeout', None)
        xmlrpclib.Transport.__init__(self, *args, **kwargs)

    def make_connection(self, *args, **kwargs):
        conn = xmlrpclib.Transport.make_connection(self, *args, **kwargs)
        if self.timeout != None: conn.timeout = self.timeout
        return conn

# http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(type):
    _instances = {}
    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]

def logtime(dt):
    """formats time like a logger does, for the csv output 
       (e.g. "2013-01-25 13:21:44,590")

    @param dt: datetime object
    @return: time string
    """
    t = time.strftime("%Y-%m-%d %H:%M:%S", dt.timetuple())
    return "%s,%03d" % (t, dt.microsecond/1000)

def time_from_cuckoomon(s):
    """parse time string received from cuckoomon via netlog

    @param s: time string
    @return: datetime object
    """
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S,%f')
