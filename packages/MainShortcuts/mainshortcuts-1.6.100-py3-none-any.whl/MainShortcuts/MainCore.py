import os
import sys
import traceback
import MainShortcuts as ms
from MainShortcuts.dictplus import dictplus


class _MainCore:
  """Переменные:
  .args - то же самое, что и sys.argv
  .dir - папка с текущей программой (использует __file__)
  .execdir - если программа находится в папке "_internal", указана родительская папка
  .embed - тексты для всраивания MainCore в программу
  .run - запущена ли программа или её импортируют? (использует __name__)"""

  def __init__(self, color: bool = True, *, __name__, __file__):
    self.args = sys.argv
    self.core_name = "MainCore"
    self.core_version = 6
    self.dir = os.path.dirname(__file__)  # Папка, в которой находится программа
    self.execdir = self.dir  # Если программа собрана через "pyinstaller --onedir", указывает папку с исполняемым файлом
    try:
      tmp = os.path.split(self.dir)
      if tmp[1] == "_internal":
        self.execdir = tmp[0]
    except:
      pass
    self.exception = traceback.format_exc  # Получить traceback в виде текста
    self.pid = os.getpid()  # PID программы
    self.run = __name__ == "__main__"  # Запущена программа или её импортируют?
    self.embed = dictplus()
    self.embed.lines = ["# MainShortcuts/mcore.begin", "from MainShortcuts.MainCore import *", "from MainShortcuts.MainCore import _MainCore", "mcore=_MainCore(__name__=__name__,__file__=__file__)", "cprint,cformat=mcore.cprint,mcore.cformat", "cfg=ms.cfg(mcore.execdir+'/cfg.json')", "cfg.default={}", "cfg.dload()", "# MainShortcuts/mcore.end"]
    self.embed.text = "\n".join(self.embed.lines) + "\n"  # Текст для встраивания MainCore в программу
    self.color_names = ["", "BG_BLACK", "BG_BLUE", "BG_GREEN", "BG_LIGHTBLACK", "BG_LIGHTBLUE", "BG_LIGHTGREEN", "BG_LIGHTPINK", "BG_LIGHTRED", "BG_LIGHTWHITE", "BG_LIGHTYELLOW", "BG_PINK", "BG_RED", "BG_WHITE", "BG_YELLOW", "BLACK", "BLUE", "GREEN", "HIGH", "LIGHTBLACK", "LIGHTBLUE", "LIGHTGREEN", "LIGHTPINK", "LIGHTRED", "LIGHTWHITE", "LIGHTYELLOW", "LOW", "PINK", "RED", "RESET", "WHITE", "YELLOW"]
    self.colors = {}
    for i in self.color_names:
      self.colors[i] = ""
    if color:
      try:
        import colorama as clr
        clr.init()
        self.colors["BG_BLACK"] = clr.Back.BLACK
        self.colors["BG_BLUE"] = clr.Back.BLUE
        self.colors["BG_GREEN"] = clr.Back.GREEN
        self.colors["BG_LIGHTBLACK"] = clr.Back.LIGHTBLACK_EX
        self.colors["BG_LIGHTBLUE"] = clr.Back.LIGHTBLUE_EX
        self.colors["BG_LIGHTGREEN"] = clr.Back.LIGHTGREEN_EX
        self.colors["BG_LIGHTPINK"] = clr.Back.LIGHTMAGENTA_EX
        self.colors["BG_LIGHTRED"] = clr.Back.LIGHTRED_EX
        self.colors["BG_LIGHTWHITE"] = clr.Back.LIGHTWHITE_EX
        self.colors["BG_LIGHTYELLOW"] = clr.Back.LIGHTYELLOW_EX
        self.colors["BG_PINK"] = clr.Back.MAGENTA
        self.colors["BG_RED"] = clr.Back.RED
        self.colors["BG_WHITE"] = clr.Back.WHITE
        self.colors["BG_YELLOW"] = clr.Back.YELLOW
        self.colors["BLACK"] = clr.Fore.BLACK
        self.colors["BLUE"] = clr.Fore.BLUE
        self.colors["GREEN"] = clr.Fore.GREEN
        self.colors["HIGH"] = clr.Style.BRIGHT
        self.colors["LIGHTBLACK"] = clr.Fore.LIGHTBLACK_EX
        self.colors["LIGHTBLUE"] = clr.Fore.LIGHTBLUE_EX
        self.colors["LIGHTGREEN"] = clr.Fore.LIGHTGREEN_EX
        self.colors["LIGHTPINK"] = clr.Fore.LIGHTMAGENTA_EX
        self.colors["LIGHTRED"] = clr.Fore.LIGHTRED_EX
        self.colors["LIGHTWHITE"] = clr.Fore.LIGHTWHITE_EX
        self.colors["LIGHTYELLOW"] = clr.Fore.LIGHTYELLOW_EX
        self.colors["LOW"] = clr.Style.DIM
        self.colors["PINK"] = clr.Fore.MAGENTA
        self.colors["RED"] = clr.Fore.RED
        self.colors["RESET"] = clr.Style.RESET_ALL
        self.colors["WHITE"] = clr.Fore.WHITE
        self.colors["YELLOW"] = clr.Fore.YELLOW
      except:
        color = False

  def __repr__(self):
    return ms.json.encode({"name": self.core_name, "version": self.core_version}, mode="c")

  def cprint(self, a: str, start: str = "", **kwargs):  # Вывести цветной текст | cprint("Обычный текст, {BLUE}Синий текст")
    try:
      b = str(a).rstrip().format(**self.colors)
    except KeyError:
      b = str(a).rstrip()
      for k, v in self.colors.items():
        try:
          arg = {k: v}
          b = b.format(**arg)
        except KeyError:
          pass
    print(self.colors["RESET"] + self.colors[start] + b.rstrip() + self.colors["RESET"], **kwargs)

  def cformat(self, a: str, start: str = "") -> str:  # Аналогично cprint, но вывод в return, и нет strip
    try:
      b = str(a).format(**self.colors)
    except KeyError:
      b = str(a).rstrip()
      for k, v in self.colors.items():
        try:
          arg = {k: v}
          b = b.format(**arg)
        except KeyError:
          pass
    return self.colors["RESET"] + self.colors[start] + b + self.colors["RESET"]

  def ctest(self):  # Вывод всех доступных цветов
    for k, v in self.colors.items():
      if k != "":
        print("{0}{1}: {2}EXAMPLE \u2591\u2592\u2593 \u2588\u2588\u2588{0}".format(self.colors["RESET"], k, v))

  def ignoreException(self, target, *args, **kwargs):
    try:
      return target(*args, **kwargs)
    except:
      return self.exception()
