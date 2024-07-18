"""Модифицированные версии встроенных значений"""
import builtins
import json


class int:
  def __init__(self, data: int = 0):
    self.data = builtins.int(data)

  def __repr__(self):
    return f"ms.values.int({json.dumps(self.data)})"

  def __str__(self):
    return builtins.str(self.data)

  def __neg__(self):
    return self.data.__neg__(self)

  def __pos__(self):
    return self.data.__pos__(self)

  def __abs__(self):
    return self.data.__abs__(self)

  def __invert__(self):
    return self.data.__invert__(self)

  def __int__(self):
    return self.data.__int__(self)

  def __float__(self):
    return self.data.__float__(self)

  def __index__(self):
    return self.data.__index__(self)

  def __trunc__(self):
    return self.data.__trunc__(self)

  def __floor__(self):
    return self.data.__floor__(self)

  def __ceil__(self):
    return self.data.__ceil__(self)

  def __add__(self, other):
    if type(self) == type(other):
      return self.data.__add__(other.data)
    else:
      return self.data.__add__(other)

  def __and__(self, other):
    if type(self) == type(other):
      return self.data.__and__(other.data)
    else:
      return self.data.__and__(other)

  def __divmod__(self, other):
    if type(self) == type(other):
      return self.data.__divmod__(other.data)
    else:
      return self.data.__divmod__(other)

  def __eq__(self, other):
    if type(self) == type(other):
      return self.data.__eq__(other.data)
    else:
      return self.data.__eq__(other)

  def __floordiv__(self, other):
    if type(self) == type(other):
      return self.data.__floordiv__(other.data)
    else:
      return self.data.__floordiv__(other)

  def __ge__(self, other):
    if type(self) == type(other):
      return self.data.__ge__(other.data)
    else:
      return self.data.__ge__(other)

  def __gt__(self, other):
    if type(self) == type(other):
      return self.data.__gt__(other.data)
    else:
      return self.data.__gt__(other)

  def __le__(self, other):
    if type(self) == type(other):
      return self.data.__le__(other.data)
    else:
      return self.data.__le__(other)

  def __lshift__(self, other):
    if type(self) == type(other):
      return self.data.__lshift__(other.data)
    else:
      return self.data.__lshift__(other)

  def __lt__(self, other):
    if type(self) == type(other):
      return self.data.__lt__(other.data)
    else:
      return self.data.__lt__(other)

  def __mod__(self, other):
    if type(self) == type(other):
      return self.data.__mod__(other.data)
    else:
      return self.data.__mod__(other)

  def __mul__(self, other):
    if type(self) == type(other):
      return self.data.__mul__(other.data)
    else:
      return self.data.__mul__(other)

  def __ne__(self, other):
    if type(self) == type(other):
      return self.data.__ne__(other.data)
    else:
      return self.data.__ne__(other)

  def __or__(self, other):
    if type(self) == type(other):
      return self.data.__or__(other.data)
    else:
      return self.data.__or__(other)

  def __radd__(self, other):
    if type(self) == type(other):
      return self.data.__radd__(other.data)
    else:
      return self.data.__radd__(other)

  def __rand__(self, other):
    if type(self) == type(other):
      return self.data.__rand__(other.data)
    else:
      return self.data.__rand__(other)

  def __rdivmod__(self, other):
    if type(self) == type(other):
      return self.data.__rdivmod__(other.data)
    else:
      return self.data.__rdivmod__(other)

  def __rfloordiv__(self, other):
    if type(self) == type(other):
      return self.data.__rfloordiv__(other.data)
    else:
      return self.data.__rfloordiv__(other)

  def __rlshift__(self, other):
    if type(self) == type(other):
      return self.data.__rlshift__(other.data)
    else:
      return self.data.__rlshift__(other)

  def __rmod__(self, other):
    if type(self) == type(other):
      return self.data.__rmod__(other.data)
    else:
      return self.data.__rmod__(other)

  def __rmul__(self, other):
    if type(self) == type(other):
      return self.data.__rmul__(other.data)
    else:
      return self.data.__rmul__(other)

  def __ror__(self, other):
    if type(self) == type(other):
      return self.data.__ror__(other.data)
    else:
      return self.data.__ror__(other)

  def __rrshift__(self, other):
    if type(self) == type(other):
      return self.data.__rrshift__(other.data)
    else:
      return self.data.__rrshift__(other)

  def __rshift__(self, other):
    if type(self) == type(other):
      return self.data.__rshift__(other.data)
    else:
      return self.data.__rshift__(other)

  def __rsub__(self, other):
    if type(self) == type(other):
      return self.data.__rsub__(other.data)
    else:
      return self.data.__rsub__(other)

  def __rtruediv__(self, other):
    if type(self) == type(other):
      return self.data.__rtruediv__(other.data)
    else:
      return self.data.__rtruediv__(other)

  def __rxor__(self, other):
    if type(self) == type(other):
      return self.data.__rxor__(other.data)
    else:
      return self.data.__rxor__(other)

  def __sub__(self, other):
    if type(self) == type(other):
      return self.data.__sub__(other.data)
    else:
      return self.data.__sub__(other)

  def __truediv__(self, other):
    if type(self) == type(other):
      return self.data.__truediv__(other.data)
    else:
      return self.data.__truediv__(other)

  def __xor__(self, other):
    if type(self) == type(other):
      return self.data.__xor__(other.data)
    else:
      return self.data.__xor__(other)


class float:
  def __init__(self, data: float = 0.0):
    self.data = builtins.float(data)

  def __repr__(self):
    return f"ms.values.float({json.dumps(self.data)})"

  def __str__(self):
    return builtins.str(self.data)

  def __neg__(self):
    return self.data.__neg__(self)

  def __pos__(self):
    return self.data.__pos__(self)

  def __abs__(self):
    return self.data.__abs__(self)

  def __int__(self):
    return self.data.__int__(self)

  def __float__(self):
    return self.data.__float__(self)

  def __trunc__(self):
    return self.data.__trunc__(self)

  def __floor__(self):
    return self.data.__floor__(self)

  def __ceil__(self):
    return self.data.__ceil__(self)

  def __add__(self, other):
    if type(self) == type(other):
      return self.data.__add__(other.data)
    else:
      return self.data.__add__(other)

  def __divmod__(self, other):
    if type(self) == type(other):
      return self.data.__divmod__(other.data)
    else:
      return self.data.__divmod__(other)

  def __eq__(self, other):
    if type(self) == type(other):
      return self.data.__eq__(other.data)
    else:
      return self.data.__eq__(other)

  def __floordiv__(self, other):
    if type(self) == type(other):
      return self.data.__floordiv__(other.data)
    else:
      return self.data.__floordiv__(other)

  def __ge__(self, other):
    if type(self) == type(other):
      return self.data.__ge__(other.data)
    else:
      return self.data.__ge__(other)

  def __gt__(self, other):
    if type(self) == type(other):
      return self.data.__gt__(other.data)
    else:
      return self.data.__gt__(other)

  def __le__(self, other):
    if type(self) == type(other):
      return self.data.__le__(other.data)
    else:
      return self.data.__le__(other)

  def __lt__(self, other):
    if type(self) == type(other):
      return self.data.__lt__(other.data)
    else:
      return self.data.__lt__(other)

  def __mod__(self, other):
    if type(self) == type(other):
      return self.data.__mod__(other.data)
    else:
      return self.data.__mod__(other)

  def __mul__(self, other):
    if type(self) == type(other):
      return self.data.__mul__(other.data)
    else:
      return self.data.__mul__(other)

  def __ne__(self, other):
    if type(self) == type(other):
      return self.data.__ne__(other.data)
    else:
      return self.data.__ne__(other)

  def __radd__(self, other):
    if type(self) == type(other):
      return self.data.__radd__(other.data)
    else:
      return self.data.__radd__(other)

  def __rdivmod__(self, other):
    if type(self) == type(other):
      return self.data.__rdivmod__(other.data)
    else:
      return self.data.__rdivmod__(other)

  def __rfloordiv__(self, other):
    if type(self) == type(other):
      return self.data.__rfloordiv__(other.data)
    else:
      return self.data.__rfloordiv__(other)

  def __rmod__(self, other):
    if type(self) == type(other):
      return self.data.__rmod__(other.data)
    else:
      return self.data.__rmod__(other)

  def __rmul__(self, other):
    if type(self) == type(other):
      return self.data.__rmul__(other.data)
    else:
      return self.data.__rmul__(other)

  def __rsub__(self, other):
    if type(self) == type(other):
      return self.data.__rsub__(other.data)
    else:
      return self.data.__rsub__(other)

  def __rtruediv__(self, other):
    if type(self) == type(other):
      return self.data.__rtruediv__(other.data)
    else:
      return self.data.__rtruediv__(other)

  def __sub__(self, other):
    if type(self) == type(other):
      return self.data.__sub__(other.data)
    else:
      return self.data.__sub__(other)

  def __truediv__(self, other):
    if type(self) == type(other):
      return self.data.__truediv__(other.data)
    else:
      return self.data.__truediv__(other)


class str:
  def __init__(self, data: str = ""):
    self.data = builtins.str(data)

  def __repr__(self):
    return f"ms.values.str({json.dumps(self.data)})"

  def __str__(self):
    return builtins.str(self.data)

  def __getitem__(self, k):
    return self.data[k]

  def __setitem__(self, k, v):
    self.data[k] = v

  def __add__(self, other):
    if type(self) == type(other):
      return self.data.__add__(other.data)
    else:
      return self.data.__add__(other)

  def __eq__(self, other):
    if type(self) == type(other):
      return self.data.__eq__(other.data)
    else:
      return self.data.__eq__(other)

  def __ge__(self, other):
    if type(self) == type(other):
      return self.data.__ge__(other.data)
    else:
      return self.data.__ge__(other)

  def __gt__(self, other):
    if type(self) == type(other):
      return self.data.__gt__(other.data)
    else:
      return self.data.__gt__(other)

  def __le__(self, other):
    if type(self) == type(other):
      return self.data.__le__(other.data)
    else:
      return self.data.__le__(other)

  def __lt__(self, other):
    if type(self) == type(other):
      return self.data.__lt__(other.data)
    else:
      return self.data.__lt__(other)

  def __mod__(self, other):
    if type(self) == type(other):
      return self.data.__mod__(other.data)
    else:
      return self.data.__mod__(other)

  def __mul__(self, other):
    if type(self) == type(other):
      return self.data.__mul__(other.data)
    else:
      return self.data.__mul__(other)

  def __ne__(self, other):
    if type(self) == type(other):
      return self.data.__ne__(other.data)
    else:
      return self.data.__ne__(other)

  def __rmod__(self, other):
    if type(self) == type(other):
      return self.data.__rmod__(other.data)
    else:
      return self.data.__rmod__(other)

  def __rmul__(self, other):
    if type(self) == type(other):
      return self.data.__rmul__(other.data)
    else:
      return self.data.__rmul__(other)


class list:
  def __init__(self, data: list = []):
    self.data = builtins.list(data)

  def __repr__(self):
    return f"ms.values.list({json.dumps(self.data)})"

  def __str__(self):
    return builtins.str(self.data)

  def __getitem__(self, k):
    return self.data[k]

  def __setitem__(self, k, v):
    self.data[k] = v

  def __add__(self, other):
    if type(self) == type(other):
      return self.data.__add__(other.data)
    else:
      return self.data.__add__(other)

  def __eq__(self, other):
    if type(self) == type(other):
      return self.data.__eq__(other.data)
    else:
      return self.data.__eq__(other)

  def __ge__(self, other):
    if type(self) == type(other):
      return self.data.__ge__(other.data)
    else:
      return self.data.__ge__(other)

  def __gt__(self, other):
    if type(self) == type(other):
      return self.data.__gt__(other.data)
    else:
      return self.data.__gt__(other)

  def __iadd__(self, other):
    if type(self) == type(other):
      return self.data.__iadd__(other.data)
    else:
      return self.data.__iadd__(other)

  def __imul__(self, other):
    if type(self) == type(other):
      return self.data.__imul__(other.data)
    else:
      return self.data.__imul__(other)

  def __le__(self, other):
    if type(self) == type(other):
      return self.data.__le__(other.data)
    else:
      return self.data.__le__(other)

  def __lt__(self, other):
    if type(self) == type(other):
      return self.data.__lt__(other.data)
    else:
      return self.data.__lt__(other)

  def __mul__(self, other):
    if type(self) == type(other):
      return self.data.__mul__(other.data)
    else:
      return self.data.__mul__(other)

  def __ne__(self, other):
    if type(self) == type(other):
      return self.data.__ne__(other.data)
    else:
      return self.data.__ne__(other)

  def __rmul__(self, other):
    if type(self) == type(other):
      return self.data.__rmul__(other.data)
    else:
      return self.data.__rmul__(other)


class dict:
  def __init__(self, data: dict = {}):
    self.data = builtins.dict(data)

  def __repr__(self):
    return f"ms.values.dict({json.dumps(self.data)})"

  def __str__(self):
    return builtins.str(self.data)

  def __getitem__(self, k):
    return self.data[k]

  def __setitem__(self, k, v):
    self.data[k] = v

  def __eq__(self, other):
    if type(self) == type(other):
      return self.data.__eq__(other.data)
    else:
      return self.data.__eq__(other)

  def __ge__(self, other):
    if type(self) == type(other):
      return self.data.__ge__(other.data)
    else:
      return self.data.__ge__(other)

  def __gt__(self, other):
    if type(self) == type(other):
      return self.data.__gt__(other.data)
    else:
      return self.data.__gt__(other)

  def __ior__(self, other):
    if type(self) == type(other):
      return self.data.__ior__(other.data)
    else:
      return self.data.__ior__(other)

  def __le__(self, other):
    if type(self) == type(other):
      return self.data.__le__(other.data)
    else:
      return self.data.__le__(other)

  def __lt__(self, other):
    if type(self) == type(other):
      return self.data.__lt__(other.data)
    else:
      return self.data.__lt__(other)

  def __ne__(self, other):
    if type(self) == type(other):
      return self.data.__ne__(other.data)
    else:
      return self.data.__ne__(other)

  def __or__(self, other):
    if type(self) == type(other):
      return self.data.__or__(other.data)
    else:
      return self.data.__or__(other)

  def __ror__(self, other):
    if type(self) == type(other):
      return self.data.__ror__(other.data)
    else:
      return self.data.__ror__(other)
