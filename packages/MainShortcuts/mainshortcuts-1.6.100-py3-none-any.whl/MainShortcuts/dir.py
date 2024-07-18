from typing import Union
import MainShortcuts.path as m_path
import os as _os
import shutil as _shutil


def create(path: str, force: bool = False) -> bool:
  """Создать папку
  Если путь существует, ничего не делает
  force - принудительно создать папку (удалит файл, который находится на её месте)"""
  if m_path.exists(path):
    type = m_path.info(path)["type"]
    if type == "dir":
      return True
    elif force:
      m_path.delete(path)
    else:
      raise Exception("The object exists and is not a folder")
  _os.makedirs(path)
  return True


mk = create


def delete(path: str):
  """Удалить папку с содержимым
  Если в назначении файл, выдаст ошибку"""
  type = m_path.info(path)["type"]
  if type == "dir":
    _shutil.rmtree(path)
  else:
    raise Exception("Unknown type: " + type)


rm = delete


def copy(fr: str, to: str, force: bool = False):
  """Копировать папку с содержимым
  force - принудительно копировать"""
  type = m_path.info(fr)["dir"]
  if type == "dir":
    if m_path.info(to)["type"] != "dir" and force:
      try:
        m_path.delete(to)
      except:
        pass
    _shutil.copytree(fr, to)
  else:
    raise Exception("Unknown type: " + type)


cp = copy


def move(fr: str, to: str, force: bool = False):
  """Переместить папку с содержимым
  force - принудительно переместить"""
  type = m_path.info(fr)["dir"]
  if type == "dir":
    if m_path.info(to)["type"] != "dir" and force:
      try:
        m_path.delete(to)
      except:
        pass
    _shutil.move(fr, to)
  else:
    raise Exception("Unknown type: " + type)


def rename(fr: str, to: str, force: bool = False):
  """Переименовать папку
  force - принудительно переименовать"""
  t = m_path.info(fr)["dir"]
  if t == "dir":
    if m_path.info(to)["type"] != "dir" and force:
      try:
        m_path.delete(to)
      except:
        pass
    _os.rename(fr, to)
  else:
    raise Exception("Unknown type: " + t)


def list(path: str = ".", extensions: Union[str, list] = None, func=None, *, files: bool = True, dirs: bool = True, links: Union[bool, None] = None):
  """Получить список содержимого папки
  files      - True: включать файлы в список
               False: не показывать файлы в списке
  dirs       - True: включать папки в список
               False: не показывать папки в списке
  links      - None: показывать всё
               True: показывать только ссылки
               False: не показывать ссылки
  extensions - список допустимых расширений (для файлов)
  func       - функция для фильтрации
               принимает путь к файлу
               возвращает True или False"""
  r = []
  for i in _os.listdir(path):
    i = f"{path}/{i}"
    if links == None:
      pass
    elif links == True:
      if not _os.path.islink(i):
        continue
    elif links == False:
      if _os.path.islink(i):
        continue
    else:
      raise Exception('"links" can only be True, False or None')
    if extensions != None and _os.path.isfile(i):
      if type(extensions) == str:
        extensions = [extensions]
      for ext in extensions:
        ext = str(ext)
        if not ext.startswith("."):
          ext = "." + ext
        if not i.endswith(ext):
          continue
    if func != None:
      if not func(i):
        continue
    if files and dirs:
      r.append(i)
      continue
    if files:
      if _os.path.isfile(i):
        r.append(i)
        continue
    if dirs:
      if _os.path.isdir(i):
        r.append(i)
        continue
  return r
