# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division, absolute_import

from run import *


def configure( path, args ):
  def cmd():
    yield 'cmake'
    for key, value in args.iteritems():
      yield '-D{0}={1}'.format( key, value )
    yield path

  run( cmd() )


