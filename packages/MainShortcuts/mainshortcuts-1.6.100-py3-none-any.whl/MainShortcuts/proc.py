import os as _os
import subprocess as _subprocess
import sys as _sys
args = _sys.argv  # Аргументы запуска программы
pid = _os.getpid()  # PID текущего процесса
var = _os.environ  # Переменные всего процесса
sp_kwargs = {
    "text": True,
    "stdin": _subprocess.PIPE,
    "stdout": _subprocess.PIPE,
    "stderr": _subprocess.PIPE,
}


def run(a, *args, **kwargs) -> dict:
  """Запустить процесс (упрощённый subprocess.Popen)"""
  kw = sp_kwargs
  kw.update(kwargs)
  p = _subprocess.Popen(a, *args, **kw)
  code = p.wait()
  out, err = p.communicate()
  r = {
      "code": code,
      "output": out,
      "out": out,
      "error": err,
      "err": err,
      "stdout": out,
      "stderr": err,
      "c": code,
      "o": out,
      "e": err,
  }
  return r
