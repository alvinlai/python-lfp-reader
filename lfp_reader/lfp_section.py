# python

# todo license
# todo copyright


"""todo
"""

import struct
import json


################################
# General

class LfpReadError(Exception):
    """File data reading error"""

class LfpSection:
    """LFP file section"""

    MAGIC          = None
    MAGIC_LENGTH   = 12
    SIZE_LENGTH    = 4        # = 16 - MAGIC_LENGTH
    SHA1_LENGTH    = 45       # = len("sha1-") + (160 / 4)
    PADDING_LENGTH = 35       # = (4 * 16) - MAGIC_LENGTH - SIZE_LENGTH - SHA1_LENGTH

    _size = None
    _sha1 = None
    _data = None
    _dpos = None
    _inf  = None

    ################
    # Internals

    def __init__(self, inf):
        self._inf = inf
        self.read()

    def __repr__(self):
        if self._size > 0:
            return "%s(%sB)" % (self.CLSNAME, self._size)
        else:
            return "%s()" % (self.CLSNAME)

    @property
    def size(self): return self._size

    @property
    def sha1(self): return self._sha1

    @property
    def data(self):
        if self._size > 0 and self._data is None:
            self._inf.seek(self._dpos, 0)
            self._data = self._inf.read(self._size)
        return self._data

    ################
    # Loading

    def read(self):
        # Read and check magic
        magic = self._inf.read(self.MAGIC_LENGTH)
        if magic != self.MAGIC:
            raise LfpReadError("Invalid magic bytes for section %s!" % self.CLSNAME)
        # Read size
        self._size = struct.unpack(">i", self._inf.read(self.SIZE_LENGTH))[0]
        if self._size > 0:
            # Read sha1
            self._sha1 = self._inf.read(self.SHA1_LENGTH)
            # Skip fixed null chars
            self._inf.read(self.PADDING_LENGTH)
            # Skip data
            self._dpos = self._inf.tell()
            self._inf.seek(self._size, 1)
            # Skip extra null chars
            ch = self._inf.read(1)
            while ch == '\0':
                ch = self._inf.read(1)
            self._inf.seek(-1, 1)
        return self


################################
# Section Types

class LfpHeader(LfpSection):
    """LFP file metadata"""
    CLSNAME = "Header"
    MAGIC = "\x89LFP\x0D\x0A\x1A\x0A\x00\x00\x00\x01"

class LfpMeta(LfpSection):
    """LFP file metadata"""
    CLSNAME = "Meta"
    MAGIC = "\x89LFM\x0D\x0A\x1A\x0A\x00\x00\x00\x00"

    _content = None

    @property
    def content(self):
        if self._content is None:
            self._content = json.loads(self.data)
        return self._content

class LfpChunk(LfpSection):
    """LFP file data chuck"""
    CLSNAME = "Chunk"
    MAGIC = "\x89LFC\x0D\x0A\x1A\x0A\x00\x00\x00\x00"

