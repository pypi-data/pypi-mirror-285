import MainShortcuts.path as m_path
import os
import shutil
import builtins
_open = builtins.open


def read(path: str, encoding: str = "utf-8", force: bool = False):
  """Прочитать файл как текст
  encoding - кодировка
  Если файла нет, возвращает пустую строку"""
  if force:
    if os.path.isfile(path):
      with _open(path, "rb") as f:
        text = f.read().decode(encoding)
    else:
      text = ""
  else:
    with _open(path, "rb") as f:
      text = f.read().decode(encoding)
  return text


def write(path: str, text: str = "", encoding: str = "utf-8", force=False):
  """Записать текст в файл
  text - текст для записи
  encoding - кодировка
  force - принудительно создать файл"""
  if os.path.isdir(path) and force:
    m_path.rm(path)
  with _open(path, "wb") as f:
    f.write(str(text).encode(encoding))
  return True


def open(path: str):
  """Прочитать файл как байты
  Если файла нет, возвращает пустые байты"""
  if os.path.isfile(path):
    with _open(path, "rb") as f:
      content = f.read()
  else:
    content = b""
  return content


load = open


def save(path: str, content=b"", force=False):
  """Записать байты в файл
  content - байты для записи
  force - принудительно создать файл"""
  if os.path.isdir(path) and force:
    m_path.rm(path)
  with _open(path, "wb") as f:
    f.write(content)
  return True


def delete(path: str):
  """Удалить файл
  Если он не существует, ничего не изменится
  Если на месте папка, выдаст ошибку"""
  type = m_path.info(path)["type"]
  if type == "file":
    m_path.rm(path)
  elif not os.path.exists(path):
    pass
  else:
    raise Exception("Unknown type: " + type)


rm = delete


def copy(fr: str, to: str, force: bool = False):
  """Копировать файл
  force - если в месте назначения папка, удалить её"""
  type = m_path.info(fr)["type"]
  if type == "file":
    if m_path.exists(to) and force:
      m_path.delete(to)
    shutil.copy(fr, to)
  else:
    raise Exception("Unknown type: " + type)


cp = copy


def move(fr: str, to: str, force: bool = False):
  """Переместить файл
  force - если в месте назначения папка, удалить её"""
  type = m_path.info(fr)["type"]
  if type == "file":
    if m_path.exists(to) and force:
      m_path.delete(to)
    shutil.move(fr, to)
  else:
    raise Exception("Unknown type: " + type)


mv = move


def rename(fr: str, to: str, force: bool = False):
  """Переименовать файл
  force - если в месте назначения папка, удалить её"""
  type = m_path.info(fr)["type"]
  if type == "file":
    if m_path.exists(to) and force:
      m_path.delete(to)
    os.rename(fr, to)
  else:
    raise Exception("Unknown type: " + type)
