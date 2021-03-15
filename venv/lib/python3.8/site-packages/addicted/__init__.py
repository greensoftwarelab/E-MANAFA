# -*- coding: utf-8 -*-
'''
Création : 30 juin 2015

@author: Eric Lapouyade
'''

__version__ = '3.0.0'

__all__ = ['Dict', 'AddDict', 'NoAttrDict', 'NoAttr']

from noattr import NoAttr
import re
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)
import types

def isgenerator(arg):
    return isinstance(arg, types.GeneratorType)

class Dict(dict):
    """
    Dict is a subclass of dict, which allows you to get AND SET(!!)
    items in the dict using the attribute syntax !

    When you previously had to write:
    my_dict = {'a': {'b': {'c': [1, 2, 3]}}}

    you can now do the same simply by:
    my_Dict = Dict()
    my_Dict.a.b.c = [1, 2, 3]

    Or for instance, if you'd like to add some additional stuff,
    where you'd with the normal dict would write
    my_dict['a']['b']['d'] = [4, 5, 6],
    you may now do the AWESOME
    my_Dict.a.b.d = [4, 5, 6]
    instead.

    update() method will *recursively* update nested dict:

    >>> d=Dict({'a':{'b':{'c':3,'d':4},'h':4}})
    >>> d.update({'a':{'b':{'c':'888'}}})
    >>> d
    {'a': {'b': {'c': '888', 'd': 4}, 'h': 4}}

    With normal dict :

    >>> d={'a':{'b':{'c':3,'d':4},'h':4}}
    >>> d.update({'a':{'b':{'c':'888'}}})
    >>> d
    {'a': {'b': {'c': '888'}}}
    """

    def __init__(self, *args, **kwargs):
        """
        If we're initialized with a dict, make sure we turn all the
        subdicts into Dicts as well.
        """
        for arg in args:
            if not arg:
                continue
            elif isinstance(arg, dict):
                for key, val in arg.items():
                    self[key] = val
            elif isinstance(arg, tuple) and (not isinstance(arg[0], tuple)):
                self[arg[0]] = arg[1]
            elif isinstance(arg, (list, tuple)) or isgenerator(arg):
                for key, val in arg:
                    self[key] = val
            else:
                raise TypeError("Dict does not understand "
                                "{0} types".format(type(arg)))

        for key, val in kwargs.items():
            self[key] = val

    def __setattr__(self, name, value):
        """
        setattr is called when the syntax a.b = 2 is used to set a value.
        """
        if hasattr(Dict, name):
            raise AttributeError("'Dict' object attribute "
                                 "'{0}' is read-only".format(name))
        else:
            self[name] = value

    def __setitem__(self, name, value):
        """
        This is called when trying to set a value of the Dict using [].
        E.g. some_instance_of_Dict['b'] = val. If 'val
        """
        value = self._hook(value)
        super(Dict, self).__setitem__(name, value)

    @classmethod
    def _hook(cls, item):
        """
        Called to ensure that each dict-instance that are being set
        is a addict Dict. Recurses.
        """
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            return type(item)(cls._hook(elem) for elem in item)
        return item

    def __getattr__(self, item):
        if item.startswith('__'):
            return super().__getattribute__(item)
        return self.__getitem__(item)

    def __getitem__(self, name):
        """
        This is called when the Dict is accessed by []. E.g.
        some_instance_of_Dict['a'];
        If the name is in the dict, we return it. Otherwise we set both
        the attr and item to a new instance of Dict.
        """
        if name not in self:
            self[name] = Dict()
        return super(Dict, self).__getitem__(name)

    def __delattr__(self, name):
        """ Is invoked when del some_addict.b is called. """
        del self[name]

    _re_pattern = re.compile('[a-zA-Z_][a-zA-Z0-9_]*')

    def __dir__(self):
        """
        Return a list of addict object attributes.
        This includes key names of any dict entries, filtered to the subset of
        valid attribute names (e.g. alphanumeric strings beginning with a
        letter or underscore).  Also includes attributes of parent dict class.
        """
        dict_keys = []
        for k in self.keys():
            if isinstance(k, str):
                m = self._re_pattern.match(k)
                if m:
                    dict_keys.append(m.string)

        obj_attrs = list(dir(Dict))

        return dict_keys + obj_attrs

    def _ipython_display_(self):
        print(str(self))    # pragma: no cover

    def _repr_html_(self):
        return str(self)

    def prune(self, prune_zero=False, prune_empty_list=True):
        """
        Removes all empty Dicts and falsy stuff inside the Dict.
        E.g
        >>> a = Dict()
        >>> a.b.c.d
        {}
        >>> a.a = 2
        >>> a
        {'a': 2, 'b': {'c': {'d': {}}}}
        >>> a.prune()
        >>> a
        {'a': 2}
        Set prune_zero=True to remove 0 values
        E.g
        >>> a = Dict()
        >>> a.b.c.d = 0
        >>> a.prune(prune_zero=True)
        >>> a
        {}
        Set prune_empty_list=False to have them persist
        E.g
        >>> a = Dict({'a': []})
        >>> a.prune()
        >>> a
        {}
        >>> a = Dict({'a': []})
        >>> a.prune(prune_empty_list=False)
        >>> a
        {'a': []}
        """
        for key, val in list(self.items()):
            if ((not val) and ((val != 0) or prune_zero) and
                    not isinstance(val, list)):
                del self[key]
            elif isinstance(val, Dict):
                val.prune(prune_zero, prune_empty_list)
                if not val:
                    del self[key]
            elif isinstance(val, (list, tuple)):
                new_iter = self._prune_iter(val, prune_zero, prune_empty_list)
                if (not new_iter) and prune_empty_list:
                    del self[key]
                else:
                    if isinstance(val, tuple):
                        new_iter = tuple(new_iter)
                    self[key] = new_iter

    @classmethod
    def _prune_iter(cls, some_iter, prune_zero=False, prune_empty_list=True):

        new_iter = []
        for item in some_iter:
            if item == 0 and prune_zero:
                continue
            elif isinstance(item, Dict):
                item.prune(prune_zero, prune_empty_list)
                if item:
                    new_iter.append(item)
            elif isinstance(item, (list, tuple)):
                new_item = type(item)(
                    cls._prune_iter(item, prune_zero, prune_empty_list))
                if new_item or not prune_empty_list:
                    new_iter.append(new_item)
            else:
                new_iter.append(item)
        return new_iter

    def to_dict(self):
        """ Recursively turn your addict Dicts into dicts. """
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else
                    item for item in value)
            else:
                base[key] = value
        return base

    def copy(self):
        """
        Return a disconnected deep copy of self. Children of type Dict, list
        and tuple are copied recursively while values that are instances of
        other mutable objects are not copied.
        """
        return Dict(self.to_dict())

    def __deepcopy__(self, memo):
        """ Return a disconnected deep copy of self. """

        y = self.__class__()
        memo[id(self)] = y
        for key, value in self.items():
            y[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return y

    def _update_kv(self,k,v):
        if ((k not in self) or
            (not isinstance(self[k], dict)) or
            (not isinstance(v, dict))):
            self[k] = v
        else:
            self[k].update(v)

    def update(self, *args, **kwargs):
        """ update() method will *recursively* update nested dict:

            >>> d=Dict({'a':{'b':{'c':3,'d':4},'h':4}})
            >>> d.update({'a':{'b':{'c':'888'}}})
            >>> d
            {'a': {'b': {'c': '888', 'd': 4}, 'h': 4}}

            please use update_dict() if you do not want this behaviour
        """
        for arg in args:
            if not arg:
                continue
            elif isinstance(arg, dict):
                for k, v in arg.items():
                    self._update_kv(k, v)
            elif isinstance(arg, (list, tuple)) and (not isinstance(arg[0], (list, tuple))):
                k = arg[0]
                v = arg[1]
                self._update_kv(k, v)
            elif isinstance(arg, (list, tuple)) or isgenerator(arg):
                for k, v in arg:
                    self._update_kv(k, v)
            else:
                raise TypeError("update does not understand "
                                "{0} types".format(type(arg)))

        for k, v in kwargs.items():
            self._update_kv(k, v)

    def update_dict(self,*args, **kwargs):
        """ not recursive update() function """
        super(Dict, self).update(*args, **kwargs)

class AddDict(Dict):
    def pprint(self):
        pp.pprint(self)

    def pformat(self):
        return pp.pformat(self)

    def find(self,pattern,**kwargs):
        dct=AddDict()
        key_prefix = kwargs.get('key_prefix','')
        deep = kwargs.get('deep',True)
        if key_prefix:
            key_prefix += '.'
        search_keys = kwargs.get('keys',True)
        search_values = kwargs.get('values',False)
        parent_values = kwargs.get('parent',False)
        parent_dict = kwargs.get('parent_dict')
        look_key = kwargs.get('look')

        for k,v in self.items():
            if search_keys:
                m = pattern.search(k)
                if m :
                    dct[key_prefix + k] = v
                    continue
            if isinstance(v,AddDict):
                if deep:
                    kwargs['key_prefix'] = key_prefix + k
                    kwargs['parent_dict'] = v
                    dct.update(v.find(pattern,**kwargs))
            elif type(v) == list:
                if deep:
                    n = 0
                    for i in v:
                        n += 1
                        if isinstance(i,AddDict):
                            kwargs['key_prefix'] = '%s%d' % (key_prefix, n)
                            kwargs['parent_dict'] = i
                            dct.update(i.find(pattern,**kwargs))
            else:
                if search_values:
                    if (not look_key) or (look_key == k) :
                        if isinstance(v,dict):
                            test_value = v.values()
                        else:
                            test_value = v
                        m = pattern.search(str(test_value))
                        if m :
                            if parent_values:
                                dct[key_prefix[:-1]] = parent_dict
                            else:
                                dct[key_prefix + k] = v
        return dct

    def count_some_values(self,pattern,ignore_case=False):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.I if ignore_case else 0)
        if callable(pattern):
            return sum(( 1 if pattern(v) else 0 for v in self.itervalues()))
        else:
            return sum(( 1 if pattern.search(str(v)) else 0 for v in self.itervalues()))

    def count_some_keys(self,pattern,ignore_case=False):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.I if ignore_case else 0)
        if callable(pattern):
            return sum(( 1 if pattern(v) else 0 for v in self.iterkeys()))
        else:
            return sum(( 1 if pattern.search(str(k)) else 0 for k in self.iterkeys()))

    def count_some_items(self,filter):
        return sum(( 1 if filter(k,v) else 0 for k,v in self.iteritems()))

    def iter_some_items(self,pattern,ignore_case=False):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.I if ignore_case else 0)
        if callable(pattern):
            return ( (k,v) for k,v in self.iteritems() if pattern(k,v) )
        else:
            return ( (k,v) for k,v in self.iteritems() if pattern.search(str(k)) )

    def iter_some_values(self,pattern,ignore_case=False):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.I if ignore_case else 0)
        if callable(pattern):
            return ( v for v in self.itervalues() if pattern(v) )
        else:
            return ( v for v in self.itervalues() if pattern.search(str(v)) )

    def iter_some_keys(self,pattern,ignore_case=False):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.I if ignore_case else 0)
        if callable(pattern):
            return ( k for k in self.iterkeys() if pattern(k) )
        else:
            return ( k for k in self.iterkeys() if pattern.search(str(k)) )

    def get_some_items(self,pattern,ignore_case=False):
        return list(self.iter_some_items(self,pattern,ignore_case))

    def get_some_values(self,pattern,ignore_case=False):
        return list(self.iter_some_values(self,pattern,ignore_case))

    def get_some_keys(self,pattern,ignore_case=False):
        return list(self.iter_some_keys(self,pattern,ignore_case))

    def mget(self,*key_list):
        if isinstance(key_list,basestring):
            key_list = key_list.split(',')
        # le string formatting veut absolument un tupple...
        return tuple([ self[k] for k in key_list ])

    def extract_keys(self,key_list):
        """ >>> d = {'a':1,'b':2,'c':3}
            >>> print d.extract_keys('b,c,d')
            >>> {'b':2,'c':3}
            >>> print d.extract_keys(['b','c','d'])
            >>> {'b':2,'c':3} """
        if isinstance(key_list,basestring):
            key_list = key_list.split(',')
        return type(self)([ (k,self[k]) for k in key_list if k in self ])

    def exclude_keys(self,key_list):
        """ >>> d = {'a':1,'b':2,'c':3}
            >>> print d.exclude_keys('b,c,d')
            >>> {'a':1}
            >>> d = {'a':1,'b':2,'c':3}
            >>> print d.exclude_keys(['b','c','d'])
            >>> {'a':1} """
        if isinstance(key_list,basestring):
            key_list = key_list.split(',')
        return type(self)([ (k,self[k]) for k in self if k not in key_list ])


    def parse_booleans(self,key_list):
        if isinstance(key_list,basestring):
            key_list = key_list.split(',')
        for k in key_list:
            if k in self:
                val = self[k]
                if isinstance(val,basestring):
                    if val.lower() == 'false':
                        self[k] = False
                    elif val.lower() == 'true':
                        self[k] = True

    def parse_numbers(self,key_list):
        if isinstance(key_list,basestring):
            key_list = key_list.split(',')
        for k in key_list:
            if k in self:
                val = self[k]
                if isinstance(val,basestring):
                    try:
                        self[k] = float(val) if '.' in val else int(val)
                    except ValueError:
                        self[k] = None

class NoAttrDict(AddDict):
    def __getitem__(self, name):
        if name not in self:
            return NoAttr
        val = super(Dict, self).__getitem__(name)
        if val is None:
            return NoAttr
        return val
