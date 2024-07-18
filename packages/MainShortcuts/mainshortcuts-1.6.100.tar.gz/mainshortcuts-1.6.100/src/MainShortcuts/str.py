from typing import Union


def array2str(a: Union[list, tuple]) -> list:
  """Преобразовать каждый элемент в строку"""
  b = []
  for i in a:
    b.append(str(i))
  return b


list2str = array2str


def dict2str(a: dict) -> dict:
  """Преобразовать каждое значение в строку"""
  b = {}
  for key, value in a.items():
    b[key] = str(value)
  return b


class replace:
  def multi(text: str, d: dict) -> str:
    """Мульти-замена {"что заменить":"чем заменить"}"""
    t = str(text)
    for k, v in d.items():
      t = t.replace(k, str(v))
    return t

  def all(text: str, fr: str, to: str) -> str:
    """Замена пока заменяемый текст не исчезнет"""
    t = str(text)
    a = str(fr)
    b = str(to)
    if a in b:
      raise Exception('"{0}" is contained in "{1}", this causes an infinite loop'.format(a, b))
    while a in t:
      t = t.replace(a, b)
    return t
