import os
import sys
from importlib import import_module
imports = {}
if hasattr(sys, "MainShortcuts_imports"):
  for i in sys.MainShortcuts_imports:
    exec(f"import {i}")
else:
  setattr(sys, "MainShortcuts_imports", [])


def riot(**t_kw):
  """Run In Another Thread"""
  import threading
  if not "daemon" in t_kw:
    t_kw["daemon"] = False

  def decorator(func):
    t_kw["target"] = func

    def wrapper(*args, **kwargs) -> threading.Thread:
      t_kw["args"] = args
      t_kw["kwargs"] = kwargs
      t = threading.Thread(**t_kw)
      t.start()
      return t
    return wrapper
  return decorator


def riop(**p_kw):
  """Run In Another Process"""
  import multiprocessing
  if not "daemon" in p_kw:
    p_kw["daemon"] = False

  def decorator(func):
    p_kw["target"] = func

    def wrapper(*args, **kwargs) -> multiprocessing.Process:
      p_kw["args"] = args
      p_kw["kwargs"] = kwargs
      p = multiprocessing.Process(**p_kw)
      p.start()
      return p
    return wrapper
  return decorator


async def async_download_file(url: str, path: str, *, ignore_status: bool = False, delete_on_error: bool = True, chunk_size: int = 1024, **kw) -> int:
  import aiohttp
  async with aiohttp.request(**kw) as resp:
    if not ignore_status:
      resp.raise_for_status()
    with open(path, "wb") as fd:
      size = 0
      try:
        async for chunk in resp.content.iter_chunked(chunk_size):
          fd.write(chunk)
          size += len(chunk)
      except:
        if delete_on_error:
          if os.path.isfile(path):
            os.remove(path)
        raise
  return size


def sync_download_file(url: str, path: str, *, ignore_status: bool = False, delete_on_error: bool = True, chunk_size: int = 1024, **kw) -> int:
  import requests
  kw["stream"] = True
  kw["url"] = url
  if not "method" in kw:
    kw["method"] = "GET"
  with requests.request(**kw) as resp:
    if not ignore_status:
      resp.raise_for_status()
    with open(path, "wb") as fd:
      size = 0
      try:
        for chunk in resp.iter_content(chunk_size):
          fd.write(chunk)
          size += len(chunk)
      except:
        if delete_on_error:
          if os.path.isfile(path):
            os.remove(path)
        raise
  return size


download_file = sync_download_file
