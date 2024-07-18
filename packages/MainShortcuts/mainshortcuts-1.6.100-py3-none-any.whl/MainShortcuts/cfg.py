import os
import builtins
import MainShortcuts.dir as m_dir
import MainShortcuts.path as m_path
noimport = {}
try:
  import MainShortcuts.file as file
except Exception as e:
  noimport["byte"] = e
  noimport["text"] = e
try:
  import MainShortcuts.json as json
except Exception as e:
  noimport["json"] = e
try:
  import pickle
except Exception as e:
  noimport["pickle"] = e
try:
  import toml
except Exception as e:
  noimport["toml"] = e
types = ["auto", "json", "pickle", "toml", "text", "byte"]


def _checkType(path: str, type: str):
  ext = m_path.info(path)["ext"].lower()
  for i in types:
    if type.lower() == i.lower():
      type = i
      break
  if not type in types:
    raise Exception('Type "{0}" not supported'.format(type))
  elif type != "auto":
    return type
  elif ext in ["json"]:
    return "json"
  elif ext in ["pickle", "pkl"]:
    return "pickle"
  elif ext in ["cpickle", "dpb"]:
    return "cPickle"
  elif ext in ["toml"]:
    return "toml"
  elif ext in ["txt"]:
    return "text"
  elif ext in ["dat", "bin"]:
    return "byte"
  else:
    raise Exception('Cannot determine type by extension "{0}"'.format(ext))


def _checkImport(type: str):
  if type in noimport:
    raise ImportError(noimport[type])
    return False
  else:
    return True


def _dict_update(a: dict, b: dict):
  for k, v in b.items():
    a[k] = v
  return a


class cfg:
  """Загрузка и сохранение данных в файл
  Рекомендуется использовать словарь"""

  def __init__(self, path: str, data: dict = {}, default: dict = {}, type: str = "auto"):
    """Аргументы:
    path - путь к файлу, в котором нужно хранить данные
    data - заранее указанные данные
    default - значения по умолчанию
    type - тип хранения (по умолчанию от расширения файла)"""
    self.path = os.path.abspath(path)
    self.data = data
    self.default = default
    self.type = _checkType(path, type)
    _checkImport(self.type)

  def __getitem__(self, k):
    return self.data[k]

  def __setitem__(self, k, v):
    self.data[k] = v

  def load(self, path: str = None, type: str = None, encoding: str = "utf-8", **kw):
    """Загрузить данные из файла
    Можно переопределить некоторые аргументы из __init__"""
    if path == None:
      path = self.path
    if type == None:
      type = self.type
    else:
      type = _checkType(path, type)
    _checkImport(type)
    if type == "json":
      kw["encoding"] = encoding
      self.data = json.read(path, **kw)
    elif type == "pickle":
      with open(path, "rb") as f:
        self.data = pickle.load(f, **kw)
    elif type == "toml":
      with open(path, "r", encoding=encoding) as f:
        self.data = toml.load(f, **kw)
    elif type == "text":
      kw["encoding"] = encoding
      self.data = file.read(path, **kw)
    elif type == "byte":
      self.data = file.open(path, **kw)
    if builtins.type(self.data) == dict:
      self.data = _dict_update(self.default, self.data)
    return self.data

  def save(self, path=None, type=None, encoding="utf-8", force=True, **kw):
    """Сохранить данные в файл
    Можно переопределить некоторые аргументы из __init__"""
    if path == None:
      path = self.path
    if type == None:
      type = self.type
    else:
      type = _checkType(path, type)
    _checkImport(type)
    if os.path.dirname(path) != "":
      m_dir.create(os.path.dirname(path), force=force)
    if type == "json":
      kw["encoding"] = encoding
      json.write(path, self.data, **kw)
    elif type == "pickle":
      with open(path, "wb") as f:
        pickle.dump(self.data, f, **kw)
    elif type == "toml":
      with open(path, "w", encoding=encoding) as f:
        toml.dump(self.data, f, **kw)
    elif type == "text":
      kw["encoding"] = encoding
      file.write(path, self.data, **kw)
    elif type == "byte":
      file.save(path, self.data, **kw)

  def set_default(self, data=None) -> dict:
    """Поставить значение по умолчанию, если оно отсутствует в данных
    Работает только для словарей"""
    if data == None:
      data = self.data.copy()
    self.data = _dict_update(self.default, data)
    return self.data

  def dload(self, data=None, *args, **kw):
    """Загрузить данные из файла и заполнить отсутствующие
    Если файла нет, устанавливаются данные по умолчанию
    Берёт те же аргументы, что и метод load"""
    if m_path.exists(self.path):
      self.load(*args, **kw)
    self.set_default(data=data)
    return self.data
  read = load
  open = load
  write = save
