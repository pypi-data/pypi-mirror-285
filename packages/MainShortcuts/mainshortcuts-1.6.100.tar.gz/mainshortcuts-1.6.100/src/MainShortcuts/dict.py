def swap(i: dict) -> dict:
  """Вывернуть словарь
  То есть поставить ключи в значения, а значения в ключи"""
  r = {}
  for k, v in i.items():
    r[v] = k
  return r


def sort(d: dict, *args, **kw) -> dict:
  """Сортировать словарь по ключам
  Принимает те же аргументы, что и list.sort"""
  keys = list(d.keys)
  keys.sort(*args, **kw)
  r = {}
  for k in keys:
    r[k] = d[k]
  return r


def reverse(d: dict) -> dict:
  """Развернуть словарь
  Начало будет в конце, конец в начале"""
  keys = list(d.keys())[::-1]
  r = {}
  for k in keys:
    r[k] = d[k]
  return r


def merge(old: dict, new: dict) -> dict:
  """Рекурсиво объединить словари"""
  out = old.copy()
  for k, v in new.items():
    if k in out:
      if type(out[k]) == dict and type(v) == dict:
        out[k] = merge(out[k], v)
      else:
        out[k] = v
    else:
      out[k] = v
  return out
