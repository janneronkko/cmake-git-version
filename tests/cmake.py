from .run import *


def configure( path, args ):
  def cmd():
    yield 'cmake'
    for key, value in args.items():
      yield '-D{0}={1}'.format( key, value )
    yield path

  run( cmd() )
