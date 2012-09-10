__author__ = 'jb'
__metaclass__ = type


class Obj(dict):
    """ Dict subclass that expose its items with attribute syntax
        It cannot access elements that have the same name as dict
        methods.
    """
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]