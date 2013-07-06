# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division, absolute_import

import cmake
import git
import testenv

import os
import re
import shutil
import tempfile
from unittest import TestCase


class GitVersionTests( TestCase ):

  def setUp( self ):
    self.path = tempfile.mkdtemp()
    os.chdir( self.path )

    git.init( 'clone' )
    os.chdir( 'clone' )
    testenv.install( 'GitVersion.cmake' )
    testenv.install( 'GitVersionCached.cmake.in' )

    createCmakeFiles()

    git.add( 'CMakeLists.txt' )
    git.add( 'GitVersion.cmake' )
    git.add( 'GitVersionCached.cmake.in' )

    git.commit( 'Add automatic version generation' )

    self._createHistory()

    self.configure()

  def headCommit( self ):
    return git.revParse( 'HEAD' )

  def configure( self, directory = 'build', cmakeArgs = {} ):
    if not os.path.isdir( directory ):
      os.mkdir( directory )

    os.chdir( directory )

    cmake.configure( '..', args = cmakeArgs )

    self.results = parseValueFile( os.path.join( '..', 'results.cmake' ) )

    os.chdir( '..' )

  def tearDown( self ):
    shutil.rmtree( self.path )

  def _createHistory( self ):
    pass

  def testVersionWithoutTag( self ):
    self.assertEqual( self.headCommit(), self.results[ 'CommitSha' ] )
    self.assertEqual( self.headCommit(), self.results[ 'Version' ] )

  def testTaggedVersion( self ):
    createCommit( 'f1.txt' )
    git.tag( '1.0', message = 'Version 1.0' )

    self.configure( 'build' )

    self.assertEqual( self.headCommit(), self.results[ 'CommitSha' ] )
    self.assertEqual( '1.0', self.results[ 'Version' ] )

  def testTaggedVersionWithAdditionalChanges( self ):
    createCommit( 'f1.txt' )
    git.tag( '1.0', message = 'Version 1.0' )
    createCommit( 'f2.txt' )
    createCommit( 'f3.txt' )

    self.configure( 'build' )

    self.assertEqual( self.headCommit(), self.results[ 'CommitSha' ] )
    self.assertRegexpMatches( self.results[ 'Version' ], r'1.0-2-g[0-9a-f]+' )


  def testCachedVersion( self ):
    createCommit( 'f1.txt' )
    git.tag( '1.0', message = 'Version 1.0' )

    self.configure( 'build2' )

    commit = self.headCommit()
    shutil.rmtree( os.path.join( '.git' ) )

    self.configure( 'cached-build' )

    self.assertEqual( commit, self.results[ 'CommitSha' ] )
    self.assertEqual( '1.0', self.results[ 'Version' ] )

  def testCustomGitDescribeArguments( self ):
    createCommit( 'f1.txt' )
    git.tag( '1.0', message = 'Version 1.0' )
    createCommit( 'f2.txt' )
    git.tag( 'pre-2.0' )
    createCommit( 'f3.txt' )

    self.configure( 'build2', cmakeArgs = { 'GIT_VERSION_DESCRIBE_ARGS': '--abbrev=4;--tags' } )

    self.assertEqual( self.headCommit(), self.results[ 'CommitSha' ] )
    self.assertRegexpMatches( self.results[ 'Version' ], r'pre-2.0-1-g[0-9a-f]{4}' )


def createCommit( filename ):
  with open( filename, 'a' ) as f:
    f.write( 'Line\n' )

  git.add( filename )
  git.commit( 'Dummy commit: {0}'.format( filename ) )

def createCmakeFiles():
  print( 'Creating CMakeLists.txt' )
  with open( 'CMakeLists.txt', 'w' ) as f:
    f.write( CMakeListsFile )

def parseValueFile( path ):
  ValueLineRe = re.compile( r'(?P<key>[^=]+)=(?P<value>.*)' )

  results = {}

  with open( path, 'r' ) as f:
    for line in f:
      line = line.strip()
      m = ValueLineRe.match( line )
      if m is not None:
        results[ m.group( 'key' ) ] = m.group( 'value' )

  return results


CMakeListsFile = '''

cmake_minimum_required( VERSION 2.8 )

project( GitVersionTest )

include( GitVersion.cmake )

GitVersionResolveVersion( Version CommitSha )

file( WRITE results.cmake "Version=${Version}\nCommitSha=${CommitSha}\n" )

'''

