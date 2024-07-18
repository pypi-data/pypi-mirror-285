from typing import *
from __future__ import annotations
def var(value: Any):
    if isinstance(value, float): return Float(value)
    if isinstance(value, str): return Str(value)
    if isinstance(value, list): return List(value)
    if isinstance(value, tuple): return Tuple(value)
    if isinstance(value, dict): return Dict(value)
    if isinstance(value, set): return Set(value)
class Float:
    """Float class in Python, with truncating .0"""
    def __init__(self, value): self.value = float(value)
    def as_integer_ratio(self) -> Tuple[int, int]: return self.value.as_integer_ratio(self)
    def hex(self) -> str: return self.value.hex(self)
    def is_integer(self) -> bool: return self.value.is_integer(self)
    @classmethod
    def fromhex(self, string: str) -> Float: return self.value.fromhex(string)
    @property
    def real(self) -> Float: return self.value.real(self)
    @property
    def imag(self) -> Float: return self.value.imag(self)
    def conjugate(self) -> Float: return self.value.conjugate(self)
    def __add__(self, value: float)      -> Float:      return (self.value.__add__(value))
    def __sub__(self, value: float)      -> Float:      return (self.value.__sub__(value))
    def __mul__(self, value: float)      -> Float:      return (self.value.__mul__(value))
    def __floordiv__(self, value: float) -> Float:      return (self.value.__floordiv__(value))
    def __truediv__(self, value: float)  -> Float:      return (self.value.__truediv__(value))
    def __mod__(self, value: float)      -> Float:      return (self.value.__mod__(value))
    def __float__(self)                  -> Float:      return self.value.__float__()
    def __abs__(self)                    -> Float:      return (self.value.__abs__(self))
    def __neg__(self)                    -> Float:      return (self.value.__neg__(self))
    def __pos__(self)                    -> Float:      return (self.value.__pos__(self))
    def __eq__(self, value: object)      -> bool:         return self.value.__eq__(value)
    def __ne__(self, value: object)      -> bool:         return self.value.__ne__(value)
    def __lt__(self, value: float)       -> bool:         return self.value.__lt__(value)
    def __le__(self, value: float)       -> bool:         return self.value.__le__(value)
    def __gt__(self, value: float)       -> bool:         return self.value.__gt__(value)
    def __ge__(self, value: float)       -> bool:         return self.value.__ge__(value)
    def __bool__(self)                   -> bool:         return self.value.__bool__()
    def __trunc__(self)                  -> int:          return self.value.__trunc__()
    def __ceil__(self)                   -> int:          return self.value.__ceil__()
    def __floor__(self)                  -> int:          return self.value.__floor__()
    def __int__(self)                    -> int:          return self.value.__int__()
    def __hash__(self)                   -> int:          return self.value.__hash__()
    def __str__(self)                    -> str:          return str(int(self.value)) if self % 1 == 0 else str(self.value)    
    def __repr__(self)                   -> str:          return self.__str__()
    def __getnewargs__(self)             -> Tuple[float]: return self.value.__getnewargs__()
    @overload
    def __ound__(self, ndigits: None = None) -> int: return self.value.__ound__(self, ndigits)
    @overload
    def __ound__(self, ndigits: SupportsIndex) -> Float: return (self.value.__ound__(self, ndigits))
    def __divmod__(self, value: float) -> Tuple[Float, Float]:
        result = self.value.__divmod__(value)
        return (Float(result[0]), Float(result[1]))
    @overload
    def __pow__(self, value: int) -> Float: return self.value.__pow__(value)
    @overload
    def __pow__(self, value: float) -> Union[Float, complex]:
        result = self.value.__pow__(value)
        return self.value(result) if isinstance(result, self.value) else complex(result)
    def __iadd__(self, value: float) -> Float:
        self.value = (self.value.__add__(value))
        return self
    def __isub__(self, value: float) -> Float:
        self.value = (self.value.__sub__(value))
        return self
    def __imul__(self, value: float) -> Float:
        self.value = (self.value.__mul__(value))
        return self
    def __ifloordiv__(self, value: float) -> Float:
        self.value = (self.value.__floordiv__(value))
        return self
    def __itruediv__(self, value: float) -> Float:
        self.value = (self.value.__truediv__(value))
        return self
    def __imod__(self, value: float) -> Float:
        self.value = (self.value.__mod__(value))
        return self
    def __idivmod__(self, value: float) -> Tuple[Float, Float]:
        result = self.value.__divmod__(value)
        self.value = self.value(result[0]), self.value(result[1])
        return self
    @overload
    def __ipow__(self, value: int) -> Float:
        self.value = (self.value.__pow__(value))
        return self
    @overload
    def __ipow__(self, value: float) -> Union[Float, complex]:
        result = self.value.__pow__(value)
        self.value = self.value(result) if isinstance(result, self.value) else complex(result)
        return self
class Str(str):
    """String in Python with:
            When + or +=, add containers like list and tuple with ","
            When * or *=, the string can be multiplied by a self.value, resulting like this:
                "abcd" * 1.5 == "abcdab"
            When - or -=, the string remove all occurences of the subtractor.
            When / or /=, the string will be split to n parts.
            It is mutable like a list."""
    # String operations
    def __init__(self, value): self.value = str(value)
    def __add__(self, other):  return self.value + str(other) if type(other) not in (list, tuple) else str(other)[1:-1]
    def __sub__(self, other):  return self.value.replace(str(other), "")
    def __mul__(self, other):  return self.value * int(other) + self.value[:int(len(self.value) * (other % 1))]
    def __eq__(self, other):   return self.value == other
    def __ne__(self, other):   return self.value != other
    def __lt__(self, other):   return len(self.value) < len(other)
    def __le__(self, other):   return len(self.value) <= len(other)
    def __gt__(self, other):   return len(self.value) > len(other)
    def __ge__(self, other):   return len(self.value) >= len(other)
    def __str__(self):         return self.value
    def __getitem__(self, index): return self.value[index]
    def __setitem__(self, index, value):
        self.value = list(self.value)
        self.value[index] = value
        self.value = "".join(self.value)
    def __contains__(self, item):
        if type(item) == str: return item in self.value
        if type(item) in (tuple, list): return not (False in [i in self.value for i in item])
    def __div__(self, other):
        other = int(other)
        return [self.value[i:i+other] for i in range(0, len(self.value), other)]
    # In-place string operations
    def __iadd__(self, other):
        self.value = self.__add__(other)
        return self
    def __isub__(self, other):
        self.value = self.__sub__(other)
        return self
    def __imul__(self, other):
        self.value = self.__mul__(other)
        return self
    def __idiv__(self, other):
        other = int(other)
        self.value = self.__div__(other)
        return self

class List(list):
    # Sequence
    """List in Python, with:
            When + or +=, it appends the add to the list. If its a container, it joines 2 lists or containers to one.
            When - or -=. it deletes all occurences of the subtractor.
            When * or *=, it can be multiplied with a self.value, like this:
                [1, 2, 3, 4] * 1.5 == [1, 2, 3, 4, 1, 2]
            When / or /=, it splits the list to n equal parts."""
    def __init__(self, value):           self.value = list(value)
    def __len__(self):                   return len(self.value)
    def __getitem__(self, index):        return self.value[index]
    def __setitem__(self, index, value): self.value[index] = value
    def __delitem__(self, index):        del self.value[index]
    def __iter__(self):                  return self.value.__iter__()
    def __reversed__(self):              return self.value[::-1]
    def __concat__(self, other):         return self.value + [other] if type(other) not in (tuple, list) else self.value + other
    def __add__(self, other):            return self.__concat__(other)
    def __eq__(self, other):             return self.value == other
    def __ne__(self, other):             return self.value != other
    def __lt__(self, other):             return len(self.value) < len(other)
    def __le__(self, other):             return len(self.value) <= len(other)
    def __gt__(self, other):             return len(self.value) > len(other)
    def __ge__(self, other):             return len(self.value) >= len(other)
    def __mul__(self, other):            return self.value * int(other) + self.value[:int(len(self.value) * (other % 1))]
    def append(self, item):              self.value.append(item)
    def extend(self, iterable):          self.value.extend(iterable)
    def insert(self, index, item):       self.value.insert(index, item)
    def remove(self, item):              self.value.remove(item)
    def pop(self, index=-1):             return self.value.pop(index)
    def clear(self):                     self.value = []
    def sort(self, *, key=None, reverse=False): self.value.sort(key, reverse)
    def reverse(self):                   return self.value[::-1]
    def __list__(self):                  return self.value
    def __str__(self):                   return str(self.value)
    def __sub__(self, other):
        a = self.value
        try:
            while 1:
                self.value.remove(other)
        except:
            b = self.value
            self.value = a
            return b
    def __div__(self, other):
        other = int(other)
        return [self.value[i:i+other] for i in range(0, len(self.value), other)]
    # In-place sequence operations
    def __iadd__(self, other):
        #print(self.__add__(oth))
        self.value = self.__add__(other)
        return self
    def __isub__(self, other):
        self.value = self.__sub__(other)
        return self
    def __imul__(self, other):
        self.value = self.__mul__(other)
        return self
    def __idiv__(self, other):
        other = int(other)
        self.value = self.__div__(other)
        return self
    # Membership
    def __contains__(self, item):
        if type(item) in (tuple, list):
            for i in range(0, len(self.value) - len(item) + 1):
                if self.value[i:i+len(item)] == item:
                    return True
            return False
        else:
            return item in self.value
class Tuple(tuple):
    # Sequence
    """Tuple in Python, with:
            All properties in List()
            Immutable"""
    def __init__(self, value):    self.value = list(value)
    def __len__(self):            return len(self.value)
    def __getitem__(self, index): return self.value[index]
    def __delitem__(self, index): del self.value[index]
    def __iter__(self):           return self.value.__iter__()
    def __reversed__(self):       return self.value[::-1]
    def __concat__(self, other):  return self.value + [other] if type(other) not in (tuple, list) else self.value + other
    def __add__(self, other):     self.__concat__(other)
    def __mul__(self, other):     return self.value * int(other) + self.value[:int(len(self.value) * (other % 1))]
    def __eq__(self, other):      return self.value == other
    def __ne__(self, other):      return self.value != other
    def __lt__(self, other):      return len(self.value) < len(other)
    def __le__(self, other):      return len(self.value) <= len(other)
    def __gt__(self, other):      return len(self.value) > len(other)
    def __ge__(self, other):      return len(self.value) >= len(other)
    def reverse(self):            return self.value[::-1]
    def __tuple__(self):          return tuple(self.value)
    def __str__(self):            return str(tuple(self.value))
    def __sub__(self, other):
        a = self.value
        try:
            while 1:
                self.value.remove(other)
        except:
            b = self.value
            self.value = a
            return b
    def __div__(self, other):
        other = int(other)
        return [self.value[i:i+other] for i in range(0, len(self.value), other)]
    # Membership
    def __contains__(self, item):
        if type(item) in (tuple, list):
            for i in range(0, len(self.value) - len(item) + 1):
                if self.value[i:i+len(item)] == item:
                    return True
            return False
        else:
            return item in self.value
class Dict(dict):
    """Dictionary in Python, with:
            When + or +=: Equvalent to dict.update but more useful types (if its not dict then dict[key] = None)
            When - or -=: Remove the element from dict and returning it else None
            When / or /=: Split dict to n parts"""
    def __init__(self, value): self.value = dict(value)
    # Mapping
    def __getitem__(self, key):               return self.value.__getitem__(key)
    def __setitem__(self, key, value):        self.value.__setitem__(key, value)
    def __delitem__(self, key):               self.value.__delitem__(key)
    def __contains__(self, key):              return self.value.__contains__(key)
    def get(self, key, default=None):         return self.value.get(key, default)
    def setdefault(self, key, default=None):  return self.value.setdefault(key, default)
    def pop(self, key, default=None):         return self.value.pop(key, default)
    def popitem(self):                        return self.value.popitem()
    def update(self, other=(), **kwargs):     self.value.update(other, **kwargs)
    def clear(self):                          self.value.clear()
    def copy(self):                           return self.value.copy()
    def fromkeys(self, iterable, value=None): return self.value.fromkeys(iterable, value)
    def items(self):                          return self.value.items()
    def keys(self):                           return self.value.keys()
    def values(self):                         return self.value.values()
    def __dict__(self):                       return dict(self.value)
    def __str__(self):                        return str(dict(self))
    def __sub__(self, key):                   return self.pop(key, None)
    def __add__(self, other):
        new_dict = Dict(self)
        if type(other) == dict:
            new_dict.update(other)
        else:
            new_dict[other] = None
        return new_dict
    def __truediv__(self, n):
        items = list(self.items())
        part_size = len(items) // n
        remainder = len(items) % n
        result = []
        start = 0
        for i in range(n):
            part_length = part_size + (1 if i < remainder else 0)
            result.append(Dict(items[start:start + part_length]))
            start += part_length      
        return result
    def __iadd__(self, other):
        self.update(other)
        return self
    def __isub__(self, key):
        if key in self:
            del self[key]
        return self
    def __eq__(self, other):
        if isinstance(other, dict):
            return self.value.__eq__(other)
        return NotImplemented


class Set(set):
    """Set in Python
        IN DEVELOPMENT"""
    def __init__(self, value):
        self.value = value
    # Set operations
    def __and__(self, other): return (self.value.__and__(other))
    def __or__(self, other): return (self.value.__or__(other))
    def __xor__(self, other): return (self.value.__xor__(other))
    def __sub__(self, other): return (self.value.__sub__(other))
    # In-place set operations
    def __iand__(self, other):
        self.value.__iand__(other)
        return self
    def __ior__(self, other):
        self.value.__ior__(other)
        return self
    def __ixor__(self, other):
        self.value.__ixor__(other)
        return self
    def __isub__(self, other):
        self.value.__isub__(other)
        return self
    # Comparison
    def __eq__(self, other): return self.value.__eq__(other)
    def __ne__(self, other): return not self.__eq__(other)
    def __lt__(self, other): return self.value.__lt__(other)
    def __le__(self, other): return self.value.__le__(other)
    def __gt__(self, other): return self.value.__gt__(other)
    def __ge__(self, other): return self.value.__ge__(other)
    # Membership
    def __contains__(self, item): return self.value.__contains__(item)
    # Mutation
    def add(self, item):
        self.value.add(item)
    def remove(self, item):
        self.value.remove(item)
    def discard(self, item):
        self.value.discard(item)
    def pop(self): return self.value.pop()
    def clear(self):
        self.value.clear()
    def update(self, *others):
        for other in others:
            self.value.update(other)
    def intersection_update(self, *others):
        self.value.intersection_update(*others)
    def difference_update(self, *others):
        self.value.difference_update(*others)
    def symmetric_difference_update(self, other):
        self.value.symmetric_difference_update(other)
    # Conversion
    def __set__(self): return set(self)
    # String representation
    def __str__(self): return str(set(self))
    # Custom operators
    def __add__(self, other):
        if isinstance(other, ):
            return (self.union(other))
        else:
            raise TypeError("Unsupported operand type(s) for +: '' and '{}'".format(type(other)))
    def __sub__(self, other):
        if isinstance(other, ):
            return (self.difference(other))
        else:
            raise TypeError("Unsupported operand type(s) for -: '' and '{}'".format(type(other)))
    def __truediv__(self, n):
        items = list(self)
        part_size = len(items) // n
        remainder = len(items) % n
        result = []
        start = 0
        for i in range(n):
            part_length = part_size + (1 if i < remainder else 0)
            result.append((items[start:start + part_length]))
            start += part_length
        return result
if __name__ == "__main__":
    pass