import functools
import os
import re
import shutil
import tempfile
from unittest import TestCase

from . import cmake
from . import git
from . import testenv


class GitVersionTests(TestCase):
    def setUp(self):
        super().setUp()

        self.path = tempfile.mkdtemp()
        self.addCleanup(functools.partial(
            shutil.rmtree,
            self.path,
        ))
        os.chdir(self.path)

    def initialize_git_clone(
        self,
        directory='clone',
        git_version_dir=None,
    ):
        git.init(directory)
        os.chdir(directory)

        git_version_cmake = 'GitVersion.cmake'
        if git_version_dir is None:
            git_version_dir = '.'

        else:
            git_version_cmake = f'{git_version_dir}/{git_version_cmake}'

        if not os.path.isdir(git_version_dir):
            os.mkdir(git_version_dir)

        testenv.install('GitVersion.cmake', git_version_dir)
        testenv.install('GitVersionCached.cmake.in', git_version_dir)

        create_cmake_files(git_version_cmake=git_version_cmake)

        git.add('CMakeLists.txt')
        git.add(os.path.join(git_version_dir, 'GitVersion.cmake'))
        git.add(os.path.join(git_version_dir, 'GitVersionCached.cmake.in'))

        git.commit('Add automatic version generation')

    def head_commit(self):
        return git.rev_parse('HEAD')

    def configure(
        self,
        directory='build',
        cmake_args={},
    ):
        if not os.path.isdir(directory):
            os.mkdir(directory)

        os.chdir(directory)

        cmake.configure('..', args=cmake_args)

        self.results = parse_value_file(os.path.join('..', 'results.cmake'))

        os.chdir('..')

    def test_version_without_tag(self):
        self.initialize_git_clone()
        self.configure()

        self.assertEqual(self.head_commit(), self.results['CommitSha'])
        self.assertEqual(self.head_commit(), self.results['Version'])

    def test_tagged_version(self):
        self.initialize_git_clone()
        self.configure()

        create_commit('f1.txt')
        git.tag('1.0', message='Version 1.0')

        self.configure('build')

        self.assertEqual(self.head_commit(), self.results['CommitSha'])
        self.assertEqual('1.0', self.results['Version'])

    def test_tagged_version_with_additional_changes(self):
        self.initialize_git_clone()
        self.configure()

        create_commit('f1.txt')
        git.tag('1.0', message='Version 1.0')
        create_commit('f2.txt')
        create_commit('f3.txt')

        self.configure('build')

        self.assertEqual(self.head_commit(), self.results['CommitSha'])
        self.assertRegexpMatches(self.results['Version'], r'1.0-2-g[0-9a-f]+')


    def testCachedVersion(self):
        self.initialize_git_clone()
        self.configure()

        create_commit('f1.txt')
        git.tag('1.0', message='Version 1.0')

        self.configure('build2')

        commit = self.head_commit()
        shutil.rmtree(os.path.join('.git'))

        self.configure('cached-build')

        self.assertEqual(commit, self.results['CommitSha'])
        self.assertEqual('1.0', self.results['Version'])

    def testCustomGitDescribeArguments(self):
        self.initialize_git_clone()
        self.configure()

        create_commit('f1.txt')
        git.tag('1.0', message='Version 1.0')
        create_commit('f2.txt')
        git.tag('pre-2.0')
        create_commit('f3.txt')

        self.configure('build2', cmake_args={'GIT_VERSION_DESCRIBE_ARGS': '--abbrev=4;--tags'})

        self.assertEqual(self.head_commit(), self.results['CommitSha'])
        self.assertRegexpMatches(self.results['Version'], r'pre-2.0-1-g[0-9a-f]{4}')

    def testSubProjectVersion(self):
        self.initialize_git_clone()
        self.configure()

        git.tag('project-1.0', message='project-1.0')

        self.initialize_git_clone('subproject')
        git.tag('subproject-1.0', message='subproject-1.0')
        os.chdir('..')
        with open('CMakeLists.txt', 'a') as f:
            f.write('add_subdirectory(subproject)\n\n')

        self.configure('build')

        sub_project_results = parse_value_file(os.path.join('subproject', 'results.cmake'))

        self.assertEqual(self.results['Version'], 'project-1.0')
        self.assertEqual(sub_project_results['Version'], 'subproject-1.0')

    def testUsingFromSubdirectory(self):
        self.initialize_git_clone(git_version_dir='gitversion')
        self.configure()


def create_commit(filename):
  with open(filename, 'a') as f:
    f.write('Line\n')

  git.add(filename)
  git.commit('Dummy commit: {0}'.format(filename))


def create_cmake_files(git_version_cmake = 'GitVersion.cmake'):
  print('Creating CMakeLists.txt')

  data = CMakeListsFile.format(
    git_version_cmake=git_version_cmake,
  )
  with open('CMakeLists.txt', 'w') as f:
    f.write(data)


def parse_value_file(path):
  value_line_re = re.compile(r'(?P<key>[^=]+)=(?P<value>.*)')

  results = {}

  with open(path, 'r') as f:
    for line in f:
      line = line.strip()
      m = value_line_re.match(line)
      if m is not None:
        results[m.group('key')] = m.group('value')

  return results


CMakeListsFile = '''

cmake_minimum_required(VERSION 3.0)

project(GitVersionTest)

include({git_version_cmake})

GitVersionResolveVersion(Version CommitSha)

file(WRITE results.cmake "Version=${{Version}}\nCommitSha=${{CommitSha}}\n")

'''

