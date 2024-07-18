import builtins
import os
import MainShortcuts.file as m_file
import MainShortcuts.path as m_path
try:
  import json5
except:
  json5 = None
import json
import sys as sys


def _obj_encoder(obj, recurse=2, func=lambda k: not k.startswith("_")) -> dict:
  """Преобразование объекта в словарь
  obj - сам объект
  recurse - глубина рекурсивной обработки
  func - фильтр атрибутов"""
  if hasattr(obj, "to_dict"):
    to_dict = getattr(obj, "to_dict")
    if callable(to_dict):
      return to_dict()
  types = [
      str,
      dict,
      tuple,
      list,
      int,
      float,
      type(True),
      type(False),
      type(None),
  ]
  d = {}
  for k in dir(obj):
    if func(k):
      v = getattr(obj, k)
      if callable(v):
        continue
      if type(v) in types:
        d[k] = v
      elif recurse > 0:
        d[k] = _obj_encoder(v, recurse=recurse - 1)
  return d


def encode(data, mode: str = "c", indent: int = 2, sort: bool = True, force: bool = False, **kw) -> str:
  """Данные в текст JSON
  data - данные для кодирования
  mode - c/compress/min/zip: сжатый JSON
         p/pretty/max/print: развёрнутый JSON
  indent - кол-во отступов в развёрнутом JSON
  sort - сортировка словарей
  force - преобразовывать объекты в словари
  остальные аргументы как в json.dumps"""
  if force:
    kw["default"] = _obj_encoder
  kw["sort_keys"] = sort
  if mode in ["c", "compress", "min", "zip"]:  # Сжатый
    kw["separators"] = [",", ":"]
  elif mode in ["pretty", "p", "print", "max"]:  # Развёрнутый
    kw["indent"] = int(indent)
  return json.dumps(data, **kw)


def decode(text: str, **kw):
  """Текст JSON в данные
  text - текст для декодирования
  остальные аргументы как в json.loads"""
  if json5 != None:
    return json5.loads(str(text), **kw)
  return json.loads(str(text), **kw)


def write(path: str, data, encoding: str = "utf-8", force: bool = False, **kw):
  """Записать данные в файл JSON
  path - путь к файлу
  data - данные
  encoding - кодировка
  force - если в месте назначения папка, удалить её
  остальные аргументы как в ms.json.encode"""
  f_kw = {}
  f_kw["encoding"] = encoding
  f_kw["force"] = force
  f_kw["path"] = path
  f_kw["text"] = encode(data, **kw)
  return m_file.write(**f_kw)


def read(path: str, encoding: str = "utf-8", **kw):
  """Прочитать данные из JSON файла
  path - путь к файлу
  encoding - кодировка
  остальные аргументы как в ms.json.decode"""
  return decode(m_file.read(path, encoding=encoding, force=False), **kw)


def print(data, file=sys.stdout, mode: str = "p", **kw):
  """Вывести данные в stdout в виде JSON
  mode - как в ms.json.encode
  file - как в print"""
  kw["mode"] = mode
  builtins.print(encode(data, **kw), file=file)


def rebuild(text: str, **kw):
  """Перестроить текст JSON
  text - сам текст
  остальные аргументы как в ms.json.encode"""
  return encode(decode(text), **kw)


def rewrite(path: str, encoding: str = "utf-8", **kw):
  """Перестроить JSON в файле
  path - путь к файлу
  encoding - кодировка
  остальные аргументы как в ms.json.write"""
  kw["encoding"] = encoding
  return write(path, read(path, encoding=encoding), **kw)
