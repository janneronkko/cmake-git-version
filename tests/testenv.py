import os.path
import shutil
import tempfile


class TempDirectory( object ):
  def __init__( self ):
    object.__init__( self )

    self.path = None

  def __enter__( self ):
    self.path = tempfile.mkdtemp()

    return self

  def __exit__( self, excType, excValue, traceback ):
    shutil.rmtree( self.path )

def getFile( name ):
  directory = os.path.dirname( os.path.dirname( __file__ ) )

  return os.path.join( directory, name )

def install( filename, dest = '.' ):
  print( 'Copying {0} to {1}'.format( filename, dest ) )
  shutil.copy( getFile( filename ), dest )
