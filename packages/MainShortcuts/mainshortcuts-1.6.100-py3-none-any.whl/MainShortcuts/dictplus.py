class dictplus:
  """Улучшенный словарь
  Можно получить элементы и через dictplus["key"], и через dictplus.key
  Вариант использования через аттрибуты может работать не на все ключи"""

  def __init__(self, data: dict = None):
    """Без аргументов создаётся {}
    Аргументом можно указать любой словарь"""
    if data == None:
      self.__data__ = {}
    else:
      self.__data__ = data.copy()

  def __getattr__(self, k):
    if k == "__data__":
      return self.__dict__[k]
    else:
      return self[k]

  def __setattr__(self, k, v):
    if k == "__data__":
      self.__dict__[k] = v
    else:
      self[k] = v

  def __repr__(self):
    return f"dictplus({str(self.__data__)})"

  def __dir__(self):
    return list(self.__data__.keys()) + ["__data__"]

  def __len__(self):
    return len(self.__data__.keys())

  def __contains__(self, k):
    return (k in self.__data__)
  __hasattr__ = __contains__

  def __eq__(self, o):
    if type(o) == dict:
      return self.__data__ == o
    else:
      return self.__data__ == o.__data__

  def __getitem__(self, k):
    return self.__dict__["__data__"][k]

  def __setitem__(self, k, v):
    self.__dict__["__data__"][k] = v

  def __delitem__(self, k):
    self.__dict__["__data__"].pop(k)

  def __delattr__(self, k):
    self.__dict__["__data__"].pop(k)
