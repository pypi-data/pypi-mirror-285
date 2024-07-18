

class EOFormula:
    """
    This class represents a formula that can be used to query the EarthOS API.
    It provides pythonic operators for building the formula, and should be
    used in conjunction with EOVar and EOFunc objects to build the formula.
    """

    def __init__(self, left, operator, right):
        self._left = left
        self._operator = operator
        self._right = right
    
    def __str__(self) -> str:
        return f"({self._left!s} {self._operator!s} {self._right!s})"

    def to_string(self) -> str:
        return str(self)

    def __add__(self, other):
        return EOFormula(self, '+', other)
    
    def __radd__(self, other):
        return EOFormula(other, '+', self)
    
    def __sub__(self, other):
        return EOFormula(self, '-', other)
    
    def __rsub__(self, other):
        return EOFormula(other, '-', self)
    
    def __mul__(self, other):
        return EOFormula(self, '*', other)
    
    def __rmul__(self, other):
        return EOFormula(other, '*', self)
    
    def __truediv__(self, other):
        return EOFormula(self, '/', other)
    
    def __rtruediv__(self, other):
        return EOFormula(other, '/', self)
    
    def __pow__(self, other):
        return EOFormula(self, '^', other)

    def __rpow__(self, other):
        return EOFormula(other, '^', self)    

class EOOffset(dict):
    def __init__(self):
        self._relative = True

    def set_absolute(self):
        self._relative = False

    def set_relative(self):
        self._relative = True

    def __str__(self) -> str:
        s = '['
        if not self._relative:
            # Absolute offsets are prefixed with an at-sign
            s = '@['

        cnt = len(self)
        cur = 0
        for key, value in self.items():
            cur += 1
            s += key + ': ' + str(value)
            if cur < cnt:
                s += ','
        s += ']'
        return s


class EOVar:
    # This represents a variable in a formula
    def __init__(self, var, info={}):
        parts = var.split('.')
        self._namespace = parts[0]
        self._name = parts[1]
        self._info = info
        self._offset = None

    def to_string(self):
        s = self._namespace + '.' + self._name 
        if self._offset:
            s += str(self._offset)
        return s

    def __str__(self) -> str:
        return self.to_string()

    def __add__(self, other):
        return EOFormula(self, '+', other)
    
    def __radd__(self, other):
        return EOFormula(other, '+', self)
    
    def __sub__(self, other):
        return EOFormula(self, '-', other)
    
    def __rsub__(self, other):
        return EOFormula(other, '-', self)
    
    def __mul__(self, other):
        return EOFormula(self, '*', other)
    
    def __rmul__(self, other):
        return EOFormula(other, '*', self)
    
    def __truediv__(self, other):
        return EOFormula(self, '/', other)
    
    def __rtruediv__(self, other):
        return EOFormula(other, '/', self)

    def __pow__(self, other):
        return EOFormula(self, '^', other)

    def __rpow__(self, other):
        return EOFormula(other, '^', self) 

    def offset(self, **kwargs):
        self._offset = EOOffset()
        for key, value in kwargs.items():
            self._offset[key] = value
        return self
    
    def absolute(self, **kwargs):
        self._offset = EOOffset()
        self._offset.set_absolute()
        for key, value in kwargs.items():
            self._offset[key] = value
        return self


class EOFunc:
    """
    This class represents a function that can be used when querying the EarthOS API.
    """
    def __init__(self, name, *args):
        self._name = name
        self._args = args

    def __str__(self) -> str:
        s = self._name + '('
        cnt = len(self._args)
        cur = 0
        for arg in self._args:
            cur += 1
            s += str(arg)
            if cur < cnt:
                s += ','
        s += ')'
        return s

    def to_string(self) -> str:
        return str(self)

    def __add__(self, other):
        return EOFormula(self, '+', other)
    
    def __radd__(self, other):
        return EOFormula(other, '+', self)
    
    def __sub__(self, other):
        return EOFormula(self, '-', other)
    
    def __rsub__(self, other):
        return EOFormula(other, '-', self)
    
    def __mul__(self, other):
        return EOFormula(self, '*', other)
    
    def __rmul__(self, other):
        return EOFormula(other, '*', self)
    
    def __truediv__(self, other):
        return EOFormula(self, '/', other)
    
    def __rtruediv__(self, other):
        return EOFormula(other, '/', self)

    def __pow__(self, other):
        return EOFormula(self, '^', other)

    def __rpow__(self, other):
        return EOFormula(other, '^', self)

