import os
import shutil
try:
  import hashlib as hl
  hl_err = False
except Exception as e:
  hl_err = e


class hash:
  """Получить контрольные суммы и размер файла
  Может зависнуть при больших файлах"""

  def __init__(self, path: str):
    if hl_err != False:
      raise hl_err
    algs = [
        "blake2b",
        "blake2s",
        "md5",
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha3_224",
        "sha3_256",
        "sha3_384",
        "sha3_512",
        "sha512",
    ]
    self.size = os.path.getsize(path)
    with open(path, "rb") as f:
      b = f.read()
      for i in algs:
        self[i] = getattr(hl, i)(b).hexdigest()

  def __getitem__(self, k):
    return getattr(self, k)

  def __setitem__(self, k, v):
    setattr(self, k, v)


class fileobj:
  """Улучшенная работа с файлом
  Переменные класса:
    .content / .data / .bytes - байты файла (получить/записать)
    .text / .str - текст файла (получить/записать)
    .lines - текстовые линии файла (получить/записать)
    .size - размер файла в байтах. Если force=True и файл отсутствует, возвращает 0
    .exists - существует ли файл?"""

  def __init__(self, p: str, encoding: str = "utf-8", force: bool = False):
    """
    p - путь к файлу
    encoding - кодировка (при работе с текстом)
    force - принудительно выполнять"""
    if os.path.isdir(p) and not force:
      raise IsADirectoryError("Can't work with folder")
    self.encoding = encoding
    self.force = force
    self.path = p

  def __getattr__(self, k):
    if k in ["content", "data", "bytes"]:
      return self.open()
    elif k in ["text", "str"]:
      return self.read()
    elif k == "lines":
      return self.read().split("\n")
    elif k == "size":
      if self.force and not os.path.exists(self.path):
        return 0
      return os.path.getsize(self.path)
    elif k == "exists":
      return os.path.exists(self.path)
    elif k == "__dict__":
      return self.__dict__
    else:
      return self.__dict__[k]

  def __setattr__(self, k, v):
    nochange = [
        "checksum",
        "copy",
        "delete",
        "exists",
        "link",
        "move",
        "open",
        "read",
        "save",
        "size",
        "write",
    ]
    if k in ["content", "data", "bytes"]:
      self.save(v)
    elif k in ["text", "str"]:
      self.write(v)
    elif k == "lines":
      self.write("\n".join(list(v)))
    elif k in nochange:
      raise AttributeError("This attribute cannot be changed")
    elif k == "__dict__":
      self.__dict__ = v
    else:
      self.__dict__[k] = v

  def __getitem__(self, k):
    return self.lines[k]

  def __setitem__(self, k, v):
    self.lines[k] = v

  def __dir__(self):
    f = [
        "checksum",
        "copy",
        "delete",
        "link",
        "move",
        "open",
        "read",
        "save",
        "write",
    ]
    f2 = [
        "cp",
        "hash",
        "ln",
        "load",
        "mv",
        "rm",
    ]
    v = [
        "bytes",
        "content",
        "data",
        "encoding",
        "exists",
        "force",
        "lines",
        "path",
        "size",
        "str",
        "text",
    ]
    return v + f + f2

  def __repr__(self):
    return f"ms.fileobj('{self.path}',encoding='{self.encoding}',force={self.force})"

  def open(self) -> bytes:
    """Получить байты из файла"""
    if self.force:
      try:
        with open(self.path, "rb") as f:
          a = f.read()
      except:
        a = b""
    else:
      with open(self.path, "rb") as f:
        a = f.read()
    return a

  def save(self, v: bytes):
    """Записать байты в файл"""
    if self.force:
      if os.path.isdir(self.path):
        shutil.rmtree(self.path)
      if type(v) != bytes:
        v = str(v).encode(self.encoding)
    with open(self.path, "wb") as f:
      a = f.write(v)
    return a

  def read(self) -> str:
    """Получить текст из файла"""
    return self.open().decode(self.encoding)

  def write(self, v: str):
    """Записать текст в файл"""
    return self.save(v.encode(self.encoding))

  def delete(self):
    """Удалить файл"""
    if os.path.islink(self.path):
      os.unlink(self.path)
    elif os.path.isfile(self.path):
      os.remove(self.path)
    elif os.path.isdir(self.path):
      shutil.rmtree(self.path)

  def move(self, dest: str, follow: bool = True):
    """Переместить файл
    follow - следовать за файлом"""
    if os.path.exists(dest) and self.force:
      if os.path.islink(dest):
        os.unlink(dest)
      elif os.path.isfile(dest):
        os.remove(dest)
      elif os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.move(self.path, dest)
    if follow:
      self.path = dest

  def copy(self, dest: str, follow: bool = False):
    """Копировать файл
    follow - следовать за файлом"""
    if os.path.exists(dest) and self.force:
      if os.path.islink(dest):
        os.unlink(dest)
      elif os.path.isfile(dest):
        os.remove(dest)
      elif os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copy(self.path, dest)
    if follow:
      self.path = dest

  def link(self, dest: str):
    """Сделать символическую ссылку на файл"""
    if os.path.exists(dest) and self.force:
      if os.path.islink(dest):
        os.unlink(dest)
      elif os.path.isfile(dest):
        os.remove(dest)
      elif os.path.isdir(dest):
        shutil.rmtree(dest)
    os.symlink(self.path, dest)

  def checksum(self) -> hash:
    """Получить контрольные суммы и размер файла"""
    return hash(self.path)
  cp = copy
  hash = checksum
  ln = link
  load = open
  mv = move
  rm = delete
