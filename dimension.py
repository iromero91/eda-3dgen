from math import sqrt
import re

class Dimension():
    _nominal = None
    _min = None
    _max = None


    def __init__(self, value, tol=None):
        if isinstance(value, str):
            if '..' in value:
                self.__init__(tuple(map(float, value.split('..'))))
            elif '+-' in value:
                _val, _tol = value.split('+-')
                self.__init__(float(_val), tol=float(_tol))
            else:
                _val = float(re.split(r'[+-]',value)[0])
                _tol = tuple(sorted(map(float, re.findall(r'([+\-][0-9.]*)', value))))
                self.__init__(_val, tol=_tol)
        elif isinstance(value, (int, float)): # Value plus tolerance
            self._nominal = float(value)
            if not tol: # No tolerance
                self._max = self._min = self._nominal
            elif isinstance(tol, tuple): # Asymetric tolerance (-, +)
                self._min = self._nominal - abs(float(tol[0]))
                self._max = self._nominal + abs(float(tol[1]))
            elif isinstance(tol, (int, float)): # Symmetric tolerance
                self._min = self._nominal - float(tol)
                self._max = self._nominal + float(tol)
            else:
                raise ValueError("Bad tolerance")
        elif isinstance(value, tuple): # Range (min, [nominal], max)
            self._min = float(value[0])
            self._max = float(value[-1])
            if len(value) == 3 and value[1] is not None:
                self._nominal = float(value[1])
    
    @property
    def tol_p(self):
        if self._nominal != None:
            return self._max - self._nominal

    @property
    def tol_m(self):
        if self._nominal != None:
            return self._nominal - self._min

    @property
    def max(self):
        return self._max

    @property
    def min(self):
        return self._min

    @property
    def nom(self):
        if self._nominal != None:
            return self._nominal
        else:
            return (self._min + self._max)*0.5
    

    def __str__(self):
        if self._nominal is None:
            return str(self._min) + '..' + str(self._max)
        elif self.tol_p == self.tol_m:
            return str(self._nominal) + '+-' + str(self.tol_p)
        else:
            return (str(self._nominal) + '+' + str(self.tol_p)
                    + '-' + str(self.tol_m))

    def __repr__(self):
        return "Dimension('{}')".format(self.__str__())
            
    def __add__(self, x):
        if isinstance(x, Dimension):
            tol = self._max - self._min
            xtol = x._max - x._min
            worst_tol = tol + xtol
            rms_tol = sqrt(tol**2+xtol**2)
            _max = self._max + x._max - (worst_tol-rms_tol)/2
            _min = self._min + x._min + (worst_tol-rms_tol)/2
            if self._nominal is not None and x._nominal is not None:
                _nominal = self._nominal + x._nominal
            else:
                _nominal = None
            if _max < _min: # If we changed sign, swap max and min
                _max, _min = _min, _max
            return Dimension((_min, _nominal, _max))
        elif isinstance(x, (int, float)):
            return self + Dimension(x)
        else:
            raise ValueError()

    def __radd__(self, x):
        return self.__add__(x)

    def __sub__(self, x):
        return self + (-x)

    def __rsub__(self, x):
        return x + (-self)
    
    def __mul__(self, x):
        if isinstance(x, (int, float)):
            _max = self._max * x
            _min = self._min * x
            if self._nominal is not None: 
                _nominal = self._nominal * x
            else:
                _nominal = None
        else:
            raise ValueError()
        if _max < _min: # If we changed sign, swap max and min
            _max, _min = _min, _max
        return Dimension((_min, _nominal, _max))

    def __rmul__(self, x):
        return self.__mul__(x)

    def __neg__(self):
        return self.__mul__(-1)
