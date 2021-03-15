# -*- coding: utf-8 -*-
'''
Création : 18 juin 2010

@author: Eric Lapouyade
'''

__version__ = '0.0.9'

class NoAttrType(object):
    __name__ = 'NoAttrType'

    def __getattr__(self,attr):
        if attr in ['ljust','rjust','rfind','find','rindex','index','count']:
            return getattr('',attr)
        if attr == '__wrapped__':
            raise AttributeError
        return self

    def __setattr__(self,attr,value):
        pass

    def __getitem__(self,key):
        return self

    def __call__(self,*args,**kwargs):
        return self

    def __nonzero__(self):
        return False

    def __repr__(self):
        return 'NoAttr'

    def __str__(self):
        return ''

    def __len__(self):
        return 0
    __int__ = __len__
    __pos__ = __len__
    __neg__ = __len__

    def __add__(self,other):
        return other
    # Be carful : DO NOT define __or__ otherwise python_textops is not working properly
    #__or__ = __add__
    __xor__ = __add__
    __radd__ = __add__
    __rsub__ = __add__

    def __sub__(self,other):
        return -other

    def __mul__(self,other):
        return 0
    __pow__ = __mul__
    __lshift__ = __mul__
    #__rshift__ = __mul__
    # Be carful : DO NOT define __rshift__ otherwise python_textops is not working properly
    __floordiv__ = __mul__
    __mod__ = __mul__
    __divmod__ = __mul__
    __div__ = __mul__
    __truediv__ = __mul__
    __rmul__ = __mul__

    def items(self):
        return ()

    def get(self,attr,default=None):
        if default is None:
            return self
        else:
            return default

    def __iter__(self):
        return iter([])

    def next(self):
        raise StopIteration

    def __gt__(self,other):
        return False
    __lt__ = __gt__
    __le__ = __gt__
    __ge__ = __gt__

    def __delitem__(self,key):
        pass

    @property
    def as_list(self):
        return []

NoAttr = NoAttrType()
