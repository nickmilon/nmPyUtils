'''
Created on Nov 10, 2008

@author: nickmilon

Defines some very simple classes and methods

'''

# keep this simple no imports allowed in this module


class Error(Exception):
    pass


class DotDot(dict):
    """ A dictionary with dot notation
        example dd=DotDot()
        dd.a=1
        dd.a ==>> 1
    """
    def __init__(self, *args, **kwargs):
        super(DotDot, self).__init__(*args, **kwargs)

    def prnt(self):
        for k, v in list(self.items()):
            print ((k, v))

    def __getattr__(self, attr):
        item = self[attr]
        if isinstance(item, dict) and not isinstance(item, DotDot):
            item = DotDot(item)
        return item

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class AdHocTree(object):
    """ builds an arbitrary tree structure using object attributes
        example:
            aht= tps.AdHocTree().foo.bar
            aht ==> <AdHocTree: bar/foo/root>
        can be extended
        newtree=aht.foo.new_foo
        newtree ==>> <AdHocTree: new_foo/foo/bar/foo/root>
    """
    _slots__ = ['parent', 'name']

    def __init__(self, parent=None, name="root"):
        """ Args:parent any object instance
                :name (str) name of toplevel Node
        """
        self.parent = parent
        self.name = name

    def __call__(self, *args, **kwargs):
        """ calls _adHocCmd_ method on root's parent if exists
        """
        elements = list(self)
        try:
            cmd = elements[-1].parent.__getattribute__('_adHocCmd_')
            # we don't use get or getattr here to avoid circular references
        except AttributeError:
            raise NotImplementedError("_adHocCmd_ {:!s}".format((type(elements[-1].parent))))
        return cmd(elements[0], *args, **kwargs)

    def __getattr__(self, attr):
        return AdHocTree(self, attr)

    def __reduce__(self):
        """it is pickl-able"""
        return (self.__class__, (self.parent, self.name))

    def __iter__(self):
        """ iterates breadth-first up to root """
        curAttr = self
        while isinstance(curAttr, AdHocTree):
            yield curAttr
            curAttr = curAttr.parent

    def __reversed__(self):
        return reversed(list(self))

    def __str__(self, separator="/"):
        return self.path()

    def __repr__(self):
        return '<AdHocTree: %s>' % self.path()

    def path(self, separator="/"):
        rt = ""
        for i in reversed(self):
            rt = "%s%s%s" % (rt, i.name, separator)
        return rt[:-1]

    def root_and_path(self):
        rt = []
        curAttr = self
        while isinstance(curAttr.parent, AdHocTree) or curAttr.parent is None:
            rt.append(curAttr.name)
            curAttr = curAttr.parent
        rt.reverse()
        return (curAttr.parent, rt)


def seconds_to_DHMS(seconds, asStr=True):
    """ seconds to Days, Hours, Minutes, Seconds
        Args: seconds (int)
        AsStr:if True returs a formated string else dictionary
    """
    d = DotDot()
    d.days = seconds // (3600 * 24)
    d.hours = (seconds // 3600) % 24
    d.minutes = (seconds // 60) % 60
    d.seconds = seconds % 60
    return "{days:02d}-{hours:02d}:{minutes:02d}:{seconds:02d}".format(**d) if asStr else d
