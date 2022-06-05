from .run import run


def add(path):
  run(['git', 'add', path])


def commit(message):
  run(['git', 'commit', '-m', message])


def init(path):
  run(['git', 'init', path ] )
  run(['git', 'config', 'commit.gpgsign', 'false'], cwd=path)
  run(['git', 'config', 'tag.gpgsign', 'false'], cwd=path)


def rev_parse(ref):
  output = run(['git', 'rev-parse', ref])

  return output.split('\n')[0].rstrip()


def tag(name, message=None):
  def cmd():
    yield 'git'
    yield 'tag'
    if message is not None:
      yield '-a'
      yield '-m'
      yield message
    yield name

  run(cmd())
