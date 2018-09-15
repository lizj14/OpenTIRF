# ---------------------------------------------
# module_base.py
# the classes used as father classes for some other classes in the program.
# ---------------------------------------------


# this is a class used to implement the singleton pattern. Any singleton class can be made by inherited from it.
# Attention: this implementation will fail in concurrent situations!
# See: http://blog.csdn.net/zylcf818/article/details/5342258
# As there are so many copies of this blog on Internet, I cannot decide which is the original, just choose one that is
# earlier relatively.
class Singleton(object):
    """The class inherited to implement the Singleton Pattern.

    Attributes:
        self.objects: the dictionary from class type to the only object of the class.
    """
    objects = {}

    def __new__(cls, *args, **kwargs):
        if cls in cls.objects:
            return cls.objects[cls]['object']
        obj = object.__new__(cls)
        cls.objects[cls] = {'object': obj, 'init': False}
        setattr(cls, '__init__', cls.decorate__init(cls.__init__))
        return cls.objects[cls]['object']

    # the __init__ function should be called only once.
    @classmethod
    def decorate__init(cls, fn):
        def init__wrap(*args):
            if not cls.objects[cls]['init']:
                fn(*args)
                cls.objects[cls]['init'] = True
            return
        return init__wrap


# just use for debug, with printing function.
# the debug is for the function of singleton, not the exact classes inherited from class Singleton.
class SingletonDebug(object):
    objects = {}

    def __new__(cls, *args, **kwargs):
        if cls in cls.objects:
            return cls.objects[cls]['object']
        obj = object.__new__(cls)
        cls.objects[cls] = {'object': obj, 'init': False}
        setattr(cls, '__init__', cls.decorate__init(cls.__init__))
        return cls.objects[cls]['object']

    # the __init__ function should be called only once.
    @classmethod
    def decorate__init(cls, fn):
        def init__wrap(*args):
            if not cls.objects[cls]['init']:
                print('init')
                fn(*args)
                cls.objects[cls]['init'] = True
            else:
                print('no change')
            return
        return init__wrap
