import os.path
import shutil
import tempfile


def get_file( name ):
    directory = os.path.dirname(os.path.dirname( __file__ ))

    return os.path.join(directory, name)


def install(filename, dest = '.'):
    print(f'Copying {filename} to {dest}')

    shutil.copy(get_file(filename), dest)
