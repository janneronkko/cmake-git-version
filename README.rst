=================
cmake-git-version
=================

Overview
========

A CMake function to expose version number based on git describe output to the build.

The version information is updated automatilly when HEAD changes, i.e. you can
be sure that the version variables hold always the correct value.

In addition to reading the version from HEAD commit the version variables
are stored in a cache file that can be bundled into a source distribution,
i.e. the version info is also available when the code is not located in
git clone.

The versions are handled correctly also for gitmodules meaning that you
get the right version number also for all the sub projects.

Example
-------

.. code-block:: cmake

  cmake_minimum_required(VERSION 3.0)

  project(GitVersionTest)

  include(GitVersion.cmake)

  GitVersionResolveVersion(Version CommitSha)
  if("${Version}" STREQUAL "Version-NOTFOUND")
    message(FATAL_ERROR "No version info available.")
  endif()

  message("Version: ${Version}")
  message("CommitSha: ${CommitSha}")


Configuration Variables
=======================

Functions
=========

GitVersionResolveVersion(VersionVar CommitVar)
----------------------------------------------

  Resolves version.

  **VersionVar** will be set to the version (git describe output).
  If there is no tags, commit hash is used.

  **CommitVar** will be set to HEAD commit.

GIT_VERSION_CACHE_FILE
----------------------

  The file used as the cache file. You need to include the configured
  file to the source distribution if you want version info to be
  available outside git clone.

GIT_VERSION_DIR
---------------

  The directory containing GitVersionCached.cmake.in file. If not set
  the directory where GitVersion.cmake is located is used.

GIT_VERSION_DESCRIBE_ARGS
-------------------------

  List of arguments passed to git describe when determining version.


License
=======

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
