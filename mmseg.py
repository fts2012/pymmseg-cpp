# -*- coding: utf-8 -*-

from ctypes import *
from os.path import join, dirname, abspath, exists

mmseg = cdll.LoadLibrary(join(dirname(__file__),
                              'mmseg-cpp',
                              'mmseg.so'))

########################################
# the rmmseg::Token struct
########################################
class Token(Structure):
    _fields_ = [('_text', c_void_p),
                ('_length', c_int)]

    def text_get(self):
        return string_at(self._text, self._length)
    def text_set(self, value):
        raise AttributeError('text attribute is read only')
    text = property(text_get, text_set)

    def length_get(self):
        return self._length
    def length_set(self):
        raise AttributeError('length attribute is read only')
    length = property(length_get, length_set)


########################################
# Init function prototypes
########################################
mmseg.mmseg_load_chars.argtypes = [c_char_p]
mmseg.mmseg_load_chars.restype  = c_int

mmseg.mmseg_load_words.argtypes = [c_char_p]
mmseg.mmseg_load_words.restype  = c_int

mmseg.mmseg_dic_add.argtypes = [c_char_p, c_int, c_int]
mmseg.mmseg_dic_add.restype  = None

mmseg.mmseg_algor_create.argtypes = [c_char_p, c_int]
mmseg.mmseg_algor_create.restype  = c_void_p

mmseg.mmseg_algor_destroy.argtypes = [c_void_p]
mmseg.mmseg_algor_destroy.restype  = None

mmseg.mmseg_next_token.argtypes = [c_void_p]
mmseg.mmseg_next_token.restype  = Token


########################################
# Python API
########################################
def dict_load_chars(path):
    res = mmseg.mmseg_load_chars(path)
    if res == 0:
        return False
    return True

def dict_load_words(path):
    res = mmseg.mmseg_load_words(path)
    if res == 0:
        return False
    return True

def dict_load_defaults():
    mmseg.mmseg_load_chars(join(dirname(__file__), 'data', 'chars.dic'))
    mmseg.mmseg_load_words(join(dirname(__file__), 'data', 'words.dic'))

class Algorithm(object):
    def __init__(self, text):
        """\
        Create an Algorithm instance to segment text.
        """
        self.algor = mmseg.mmseg_algor_create(text, len(text))
        self.destroied = False

    def __iter__(self):
        """\
        Iterate through all tokens. Note the iteration has
        side-effect: an Algorithm object can only be iterated
        once.
        """
        while True:
            tk = self.next_token()
            if tk is None:
                raise StopIteration
            yield tk
    
    def next_token(self):
        """\
        Get next token. When no token available, return None.
        """
        if self.destroied:
            return None
        
        tk = mmseg.mmseg_next_token(self.algor)
        if tk.length == 0:
            # no token available, the algorithm object
            # can be destroied
            self._destroy()
            return None
        else:
            return tk

    def _destroy(self):
        
        if not self.destroied:
            mmseg.mmseg_algor_destroy(self.algor)
            self.destroied = True

    def __del__(self):
        self._destroy()
