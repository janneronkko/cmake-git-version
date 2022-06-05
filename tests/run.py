import subprocess


class RunError( Exception ):
  pass

def run( cmd, cwd=None, ):
  p = subprocess.Popen(
    cmd,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT,
    cwd = cwd,
    encoding = 'utf-8',
  )

  print( '$ {}'.format( ' '.join( map( lambda a: '"{}"'.format( a ), cmd ) ) ) )
  stdout, stderr = p.communicate()
  for line in stdout.split( '\n' ):
    print( '> {}'.format( line.rstrip() ) )

  if p.returncode != 0:
    raise RunError()

  return stdout

def runAndGetSingleValue( cmd ):
  output = run( cmd )

  return output.split( '\n' )[ 0 ].rstrip()
