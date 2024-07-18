"""Этот файл просто импортирует части модуля
Он создаётся автоматически"""
import os
import MainShortcuts.main as main
imports_all = []
imports_import_errors = {}
noimport = []
if "MS_NOIMPORT" in os.environ:
  for i in os.environ["MS_NOIMPORT"].split(","):
    if i.strip():
      noimport.append(i.strip().lower())
noimport.sort()
if not 'cd' in noimport:
  try:
    cd = main.cd
    imports_all.append('cd')
  except Exception as e:
    imports_import_errors['cd'] = e
if not 'clear_ANSI' in noimport:
  try:
    clear_ANSI = main.clear_ANSI
    imports_all.append('clear_ANSI')
  except Exception as e:
    imports_import_errors['clear_ANSI'] = e
if not 'clear' in noimport:
  try:
    clear = main.clear
    imports_all.append('clear')
  except Exception as e:
    imports_import_errors['clear'] = e
if not 'cls_ANSI' in noimport:
  try:
    cls_ANSI = main.cls_ANSI
    imports_all.append('cls_ANSI')
  except Exception as e:
    imports_import_errors['cls_ANSI'] = e
if not 'cls' in noimport:
  try:
    cls = main.cls
    imports_all.append('cls')
  except Exception as e:
    imports_import_errors['cls'] = e
if not 'exit' in noimport:
  try:
    exit = main.exit
    imports_all.append('exit')
  except Exception as e:
    imports_import_errors['exit'] = e
if not 'pwd' in noimport:
  try:
    pwd = main.pwd
    imports_all.append('pwd')
  except Exception as e:
    imports_import_errors['pwd'] = e
if not 'timedelta' in noimport:
  try:
    timedelta = main.timedelta
    imports_all.append('timedelta')
  except Exception as e:
    imports_import_errors['timedelta'] = e
if not 'randfloat' in noimport:
  try:
    randfloat = main.randfloat
    imports_all.append('randfloat')
  except Exception as e:
    imports_import_errors['randfloat'] = e
if not 'cfg' in noimport:
  try:
    from MainShortcuts.cfg import cfg
    imports_all.append('cfg')
  except Exception as e:
    imports_import_errors['cfg'] = e
if not 'dictplus' in noimport:
  try:
    from MainShortcuts.dictplus import dictplus
    imports_all.append('dictplus')
  except Exception as e:
    imports_import_errors['dictplus'] = e
if not 'fileobj' in noimport:
  try:
    from MainShortcuts.fileobj import fileobj
    imports_all.append('fileobj')
  except Exception as e:
    imports_import_errors['fileobj'] = e
if not 'dict' in noimport:
  try:
    import MainShortcuts.dict as dict
    imports_all.append('dict')
  except Exception as e:
    imports_import_errors['dict'] = e
if not 'dir' in noimport:
  try:
    import MainShortcuts.dir as dir
    imports_all.append('dir')
  except Exception as e:
    imports_import_errors['dir'] = e
if not 'file' in noimport:
  try:
    import MainShortcuts.file as file
    imports_all.append('file')
  except Exception as e:
    imports_import_errors['file'] = e
if not 'json' in noimport:
  try:
    import MainShortcuts.json as json
    imports_all.append('json')
  except Exception as e:
    imports_import_errors['json'] = e
if not 'list' in noimport:
  try:
    import MainShortcuts.list as list
    imports_all.append('list')
  except Exception as e:
    imports_import_errors['list'] = e
if not 'os' in noimport:
  try:
    import MainShortcuts.os as os
    imports_all.append('os')
  except Exception as e:
    imports_import_errors['os'] = e
if not 'path' in noimport:
  try:
    import MainShortcuts.path as path
    imports_all.append('path')
  except Exception as e:
    imports_import_errors['path'] = e
if not 'proc' in noimport:
  try:
    import MainShortcuts.proc as proc
    imports_all.append('proc')
  except Exception as e:
    imports_import_errors['proc'] = e
if not 'str' in noimport:
  try:
    import MainShortcuts.str as str
    imports_all.append('str')
  except Exception as e:
    imports_import_errors['str'] = e
if not 'utils' in noimport:
  try:
    import MainShortcuts.utils as utils
    imports_all.append('utils')
  except Exception as e:
    imports_import_errors['utils'] = e
if not 'win' in noimport:
  try:
    import MainShortcuts.win as win
    imports_all.append('win')
  except Exception as e:
    imports_import_errors['win'] = e
imports_all.sort()
