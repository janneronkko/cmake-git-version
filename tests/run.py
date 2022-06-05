import subprocess


class RunError( Exception ):
  pass

def run(cmd, cwd=None):
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        encoding='utf-8',
    )

    print('$ {}'.format(' '.join(
        arg if ' ' not in arg else f'"{arg}"'
        for arg in cmd
    )))

    stdout, stderr = p.communicate()
    for line in stdout.split('\n'):
        print(f'> {line.rstrip()}')

    if p.returncode != 0:
        raise RunError()

    return stdout
