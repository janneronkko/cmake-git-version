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

  def initializeGitClone( self, directory = 'clone', gitVersionDir = None ):
    git.init( directory )
    os.chdir( directory )

    gitversioncmake = 'GitVersion.cmake'
    if gitVersionDir is None:
      gitVersionDir = '.'
    else:
      gitversioncmake = '{0}/{1}'.format( gitVersionDir, gitversioncmake )
      if not os.path.isdir( gitVersionDir ):
        os.mkdir( gitVersionDir )

    testenv.install( 'GitVersion.cmake', gitVersionDir )
    testenv.install( 'GitVersionCached.cmake.in', gitVersionDir )

    createCmakeFiles( gitversioncmake = gitversioncmake )

    git.add( 'CMakeLists.txt' )
    git.add( os.path.join( gitVersionDir, 'GitVersion.cmake' ) )
    git.add( os.path.join( gitVersionDir, 'GitVersionCached.cmake.in' ) )

    git.commit( 'Add automatic version generation' )

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

  def testVersionWithoutTag( self ):
    self.initializeGitClone()
    self.configure()

    self.assertEqual( self.headCommit(), self.results[ 'CommitSha' ] )
    self.assertEqual( self.headCommit(), self.results[ 'Version' ] )

  def testTaggedVersion( self ):
    self.initializeGitClone()
    self.configure()

    createCommit( 'f1.txt' )
    git.tag( '1.0', message = 'Version 1.0' )

    self.configure( 'build' )

    self.assertEqual( self.headCommit(), self.results[ 'CommitSha' ] )
    self.assertEqual( '1.0', self.results[ 'Version' ] )

  def testTaggedVersionWithAdditionalChanges( self ):
    self.initializeGitClone()
    self.configure()

    createCommit( 'f1.txt' )
    git.tag( '1.0', message = 'Version 1.0' )
    createCommit( 'f2.txt' )
    createCommit( 'f3.txt' )

    self.configure( 'build' )

    self.assertEqual( self.headCommit(), self.results[ 'CommitSha' ] )
    self.assertRegexpMatches( self.results[ 'Version' ], r'1.0-2-g[0-9a-f]+' )


  def testCachedVersion( self ):
    self.initializeGitClone()
    self.configure()

    createCommit( 'f1.txt' )
    git.tag( '1.0', message = 'Version 1.0' )

    self.configure( 'build2' )

    commit = self.headCommit()
    shutil.rmtree( os.path.join( '.git' ) )

    self.configure( 'cached-build' )

    self.assertEqual( commit, self.results[ 'CommitSha' ] )
    self.assertEqual( '1.0', self.results[ 'Version' ] )

  def testCustomGitDescribeArguments( self ):
    self.initializeGitClone()
    self.configure()

    createCommit( 'f1.txt' )
    git.tag( '1.0', message = 'Version 1.0' )
    createCommit( 'f2.txt' )
    git.tag( 'pre-2.0' )
    createCommit( 'f3.txt' )

    self.configure( 'build2', cmakeArgs = { 'GIT_VERSION_DESCRIBE_ARGS': '--abbrev=4;--tags' } )

    self.assertEqual( self.headCommit(), self.results[ 'CommitSha' ] )
    self.assertRegexpMatches( self.results[ 'Version' ], r'pre-2.0-1-g[0-9a-f]{4}' )

  def testSubProjectVersion( self ):
    self.initializeGitClone()
    self.configure()

    git.tag( 'project-1.0', message = 'project-1.0' )

    self.initializeGitClone( 'subproject' )
    git.tag( 'subproject-1.0', message = 'subproject-1.0' )
    os.chdir( '..' )
    with open( 'CMakeLists.txt', 'a' ) as f:
      f.write( 'add_subdirectory( subproject )\n\n' )

    self.configure( 'build' )

    subProjectResults = parseValueFile( os.path.join( 'subproject', 'results.cmake' ) )

    self.assertEqual( self.results[ 'Version'], 'project-1.0' )
    self.assertEqual( subProjectResults[ 'Version'], 'subproject-1.0' )

  def testUsingFromSubdirectory( self ):
    self.initializeGitClone( gitVersionDir = 'gitversion' )
    self.configure()


def createCommit( filename ):
  with open( filename, 'a' ) as f:
    f.write( 'Line\n' )

  git.add( filename )
  git.commit( 'Dummy commit: {0}'.format( filename ) )

def createCmakeFiles( gitversioncmake = 'GitVersion.cmake' ):
  print( 'Creating CMakeLists.txt' )

  data = CMakeListsFile.format(
    gitversioncmake = gitversioncmake
  )
  with open( 'CMakeLists.txt', 'w' ) as f:
    f.write( data )

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

include( {gitversioncmake} )

GitVersionResolveVersion( Version CommitSha )

file( WRITE results.cmake "Version=${{Version}}\nCommitSha=${{CommitSha}}\n" )

'''

