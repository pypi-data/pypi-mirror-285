import sys
if "win" in sys.platform:
  import win32com.client
  from MainShortcuts.dictplus import dictplus
  shell = dictplus()
  shell.WScript = win32com.client.Dispatch("WScript.Shell")
  _names = dictplus()
  _names.lnk = {"args": "Arguments", "cwd": "WorkingDirectory", "desc": "Description", "hotkey": "Hotkey", "icon": "IconLocation", "lnk": "FullName", "target": "TargetPath"}

  def read_lnk(path: str) -> dictplus:
    """Читает ярлык .lnk"""
    r = dictplus()
    lnk = shell.WScript.CreateShortcut(path.replace("/", "\\"))
    r.src = lnk
    for k, v in _names.lnk.items():
      if hasattr(lnk, v):
        r[k] = getattr(lnk, v)
      else:
        r[k] = None
    return r

  def write_lnk(path: str, target: str, args: str = None, cwd: str = None, desc: str = None, hotkey: str = None, icon: str = None,):
    """Создаёт ярлык .lnk"""
    lnk = shell.WScript.CreateShortCut(path.replace("/", "\\"))
    lnk.TargetPath = target.replace("/", "\\")
    if args != None:
      lnk.Arguments = args
    if cwd != None:
      lnk.WorkingDirectory = cwd.replace("/", "\\")
    if desc != None:
      lnk.Description = desc
    if hotkey != None:
      lnk.Hotkey = hotkey
    if icon != None:
      lnk.IconLocation = icon.replace("/", "\\")
    lnk.Save()
