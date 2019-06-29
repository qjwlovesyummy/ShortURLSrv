import sys


class Const(object):

    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__.keys():
            raise self.ConstError('Can\'t change const value of \'%s\'' % key)
        elif not key.islower():
            raise self.ConstCaseError('Const Name \'%s\' not in lower case' % key)
        else:
            self.__dict__[key] = value

    def exists(self, key):
        return self.__dict__.keys().__contains__(key)


sys.modules[__name__] = Const
