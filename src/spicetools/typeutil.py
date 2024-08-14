import spiceypy as sp
import ctypes


__all__ = ['empty_double_vector', 'str2char_p']


def str2char_p(spkid):
    '''Quick `string_to_char_p` when input is convertible to string.
    Original code:
    def string_to_char_p(inobject, inlen=None):
        """
        convert a python string to a char_p

        :param inobject: input string, int for getting null string of length of int
        :param inlen: optional parameter, length of a given string can be specified
        :return:
        """
        if inlen and isinstance(inobject, str):
            return create_string_buffer(inobject.encode(encoding="UTF-8"), inlen)
        if isinstance(inobject, bytes):
            return inobject
        if isinstance(inobject, c_int):
            return string_to_char_p(" " * inobject.value)
        if isinstance(inobject, int):
            return string_to_char_p(" " * inobject)
        if isinstance(inobject, numpy.str_):
            return c_char_p(inobject.encode(encoding="utf-8"))
        return c_char_p(inobject.encode(encoding="UTF-8"))
    '''
    return sp.support_types.c_char_p(str(spkid).encode(encoding="UTF-8"))


def empty_double_vector(n):
    '''Quick `empty_double_vector` when input is python int.
    Original code:
    def empty_double_vector(n):
        if isinstance(n, c_int):
            n = n.value
        assert isinstance(n, int)
        return (c_double * n)()
    '''
    return (ctypes.c_double * n)()

