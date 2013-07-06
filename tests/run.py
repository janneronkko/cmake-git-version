# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division, absolute_import

import itertools
import subprocess


class RunError( Exception ):
  pass

def run( cmd ):
  p = subprocess.Popen(
    cmd,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT,
  )

  print( '$ {}'.format( ' '.join( itertools.imap( lambda a: '"{}"'.format( a ), cmd ) ) ) )
  stdout, stderr = p.communicate()
  for line in stdout.split( '\n' ):
    print( '> {}'.format( line.rstrip() ) )

  if p.returncode != 0:
    raise RunError()

  return stdout

def runAndGetSingleValue( cmd ):
  output = run( cmd )

  return output.split( '\n' )[ 0 ].rstrip()

