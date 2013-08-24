#
#  Copyright 2013 Janne Rönkkö (jroo@iki.fi)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#


#
# ## Overview ##
#
# Functions for determining version based on git HEAD commit and tags. The
# version information is updated always after HEAD changes, i.e. you can
# be sure that the version variables hold always the correct value.
#
# In addition to reading the version from HEAD commit the version variables
# are stored in a cache file that can be bundled into a source distribution,
# i.e. the version info is also available when the code is not located in
# git clone.
#
# The versions are handled correctly also for gitmodules meaning that you
# get the right version number also for all the sub projects.
#
# ## Configuration Variables ##
#
# GIT_VERSION_CACHE_FILE
#
#   The file used as the cache file. You need to include the configured
#   file to the source distribution if you want version info to be
#   available outside git clone.
#
# GIT_VERSION_DIR
#
#   The directory containing GitVersionCached.cmake.in file. If not set
#   the directory where GitVersion.cmake is located is used.
#
# GIT_VERSION_DESCRIBE_ARGS
#
#   List of arguments passed to git describe when determining version.
#
# ## Functions ##
#
# GitVersionResolveVersion( VersionVar CommitVar )
#
#   Resolves version.
#
#   VersionVar will be set to the version (commit hash if git describe
#   has nothing to describe).
#   CommitVar will be set to HEAD commit.
#
# ## Example CMakeLists.txt ##
#
#   cmake_minimum_required( VERSION 2.8 )
#   project( GitVersionTest )
#   include( GitVersion.cmake )
#   GitVersionResolveVersion( Version CommitSha )
#   if( "${Version}" STREQUAL "Version-NOTFOUND" )
#     message( FATAL_ERROR "No version info available." )
#   endif()
#   message( "Version: ${Version}" )
#   message( "CommitSha: ${CommitSha}" )
#


if( NOT DEFINED GIT_VERSION_CACHE_FILE )
  set(
    GIT_VERSION_CACHE_FILE
    ${CMAKE_CURRENT_SOURCE_DIR}/GitVersionCached.cmake
  )
endif()

if( NOT DEFINED GIT_VERSION_DIR )
  set( GIT_VERSION_DIR "${CMAKE_CURRENT_LIST_DIR}" )
endif()

function( GitVersionResolveVersion VersionVar CommitVar )

  macro( SetResultAndReturn )

    if( EXISTS ${GIT_VERSION_CACHE_FILE} )

      include( ${GIT_VERSION_CACHE_FILE} )
      message( STATUS "Version: ${GitVersion} (commit: ${GitHead})" )

    else()

      set( ${VersionVar} "${VersionVar}-NOTFOUND" PARENT_SCOPE )
      set( ${CommitVar} "${CommitVar}-NOTFOUND" PARENT_SCOPE )
      message( WARNING "Could not determine version." )

    endif()

    return()

  endmacro()

  find_program( GitBin git )
  if( "${GitBin}" STREQUAL "GitBin-NOTFOUND" )
    SetResultAndReturn()
  endif()

  GitVersionResolveGitdir( GitDir )
  if( "${GitDir}" STREQUAL "GitDir-NOTFOUND" )
    SetResultAndReturn()
  endif()

  GitVersionDependCmakeConfigureOnGitHead( "${GitDir}" )

  GitVersionRunGitCommand( GitHead rev-parse HEAD )
  if( ${GitHead} STREQUAL "GitHead-NOTFOUND" )
    message( FATAL_ERROR "Could not determine commit hash for HEAD." )
  endif()

  GitVersionRunGitCommand( GitDescribe describe ${GIT_VERSION_DESCRIBE_ARGS} )
  if( ${GitDescribe} STREQUAL "GitDescribe-NOTFOUND" )
    set( GitVersion ${GitHead} )
  else()
    set( GitVersion ${GitDescribe} )
  endif()

  file( REMOVE "${GIT_VERSION_CACHE_FILE}" )
  configure_file( ${GIT_VERSION_DIR}/GitVersionCached.cmake.in "${GIT_VERSION_CACHE_FILE}" @ONLY )

  SetResultAndReturn()

endfunction()

function( GitVersionDependCmakeConfigureOnGitHead GitDir )

  set( GitHeadFile "${GitDir}/HEAD" )
  file( READ "${GitHeadFile}" GitHeadFileData )
  string( STRIP "${GitHeadFileData}" GitHeadFileData )

  set( ConfGitHeadFile "${CMAKE_BINARY_DIR}/GitVersionCurrentHead" )
  configure_file( "${GitHeadFile}" "${ConfGitHeadFile}" COPYONLY )

  string( FIND "${GitHeadFileData}" "ref:" RefStrStart )
  if( NOT ${RefStrStart} EQUAL -1 )

    string( REPLACE "ref: " "${GitDir}/" GitRefFile "${GitHeadFileData}" )
    set( ConfGitRefFile "${CMAKE_BINARY_DIR}/GitVersionCurrentRef" )
    configure_file( "${GitRefFile}" "${ConfGitRefFile}" COPYONLY )

  endif()

endfunction()

function( GitVersionResolveGitdir ResultVar )

  GitVersionRunGitCommand( GitDir rev-parse --git-dir )

  if( NOT EXISTS "${GitDir}" )
    find_program( Cygpath cygpath )
    if( NOT "${Cygpath}" STREQUAL "Cygpath-NOTFOUND" )
      execute_process(
        COMMAND cygpath -m ${GitDir}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        OUTPUT_VARIABLE GitDir
        OUTPUT_STRIP_TRAILING_WHITESPACE
      )
    endif()
  endif()

  if( NOT "${GitDir}" STREQUAL "GitDir-NOTFOUND" AND IS_ABSOLUTE "${GitDir}" )
    file( RELATIVE_PATH GitDir ${CMAKE_CURRENT_SOURCE_DIR} "${GitDir}" )
  endif()

  set( ${ResultVar} "${GitDir}" PARENT_SCOPE )

endfunction()

function( GitVersionRunGitCommand ResultVarName )

  execute_process(
    COMMAND ${GitBin} ${ARGN}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    RESULT_VARIABLE ExitCode
    OUTPUT_VARIABLE Output
    ERROR_QUIET
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )

  if( ${ExitCode} EQUAL 0 )
    set( ${ResultVarName} "${Output}" PARENT_SCOPE )
  else()
    set( ${ResultVarName} "${ResultVarName}-NOTFOUND" PARENT_SCOPE )
  endif()

endfunction()

