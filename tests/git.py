from .run import *


def add( path ):
  run( [ 'git', 'add', path, ] )

def commit( message ):
  run( [ 'git', 'commit', '-m', message ] )

def init( path ):
  run( [ 'git', 'init', path ] )
  run( [ 'git', 'config', 'tag.gpgsign', 'false' ], cwd = path )

def revParse( ref ):
  return runAndGetSingleValue( [ 'git', 'rev-parse', ref ] )

def tag( name, message = None ):
  def cmd():
    yield 'git'
    yield 'tag'
    if message is not None:
      yield '-a'
      yield '-m'
      yield message
    yield name

  run( cmd() )
