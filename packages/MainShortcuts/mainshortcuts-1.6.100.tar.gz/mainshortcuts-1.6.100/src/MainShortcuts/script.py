from MainShortcuts.MainCore import ms, _MainCore
mcore = _MainCore(__file__=__file__, __name__=__name__)
cprint = mcore.cprint
cformat = mcore.cformat
argv = mcore.args[1:]


def mkdir(path=argv):
  if type(path) == str:
    p = [path]
  elif type(path) == tuple:
    p = list(path)
  else:
    p = path
  for i in p:
    try:
      ms.dir.create(i)
    except Exception as e:
      cprint(e, start="RED")


def jsonPretty(path=argv):
  if type(path) == str:
    p = [path]
  elif type(path) == tuple:
    p = list(path)
  else:
    p = path
  for i in p:
    try:
      d = ms.json.read(i)
      ms.json.write(i, d, mode="p")
    except Exception as e:
      cprint(e, start="RED")


def jsonCompress(path=argv):
  if type(path) == str:
    p = [path]
  elif type(path) == tuple:
    p = list(path)
  else:
    p = path
  for i in p:
    try:
      d = ms.json.read(i)
      ms.json.write(i, d, mode="c")
    except Exception as e:
      cprint(e, start="RED")


def getCore(path=argv):
  if type(path) == str:
    p = [path]
  elif type(path) == tuple:
    p = list(path)
  else:
    p = path
  for i in p:
    try:
      if ms.path.exists(i):
        a = ms.file.read(i)
        c = mcore.embed.text + a
        ms.file.write(i, c.rstrip())
        cprint(f'MainCore added to the beginning of the file "{i}"', start="GREEN")
      else:
        ms.file.write(i, mcore.embed.text)
        cprint(f'MainCore is written to file "{i}"', start="GREEN")
    except Exception as e:
      cprint(e, start="RED")
