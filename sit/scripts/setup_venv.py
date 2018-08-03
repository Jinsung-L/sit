import venv
import shutil
import subprocess


def venv_pip(args, venv_path, debug=False):
    commands = ['{}/bin/pip'.format(venv_path)] + args.split(' ')
    if not debug:
        return subprocess.check_output(commands).decode()
    else:
        logs = ''
        with subprocess.Popen(commands, stdout=subprocess.PIPE) as proc:
            while proc.poll() is None:
                log = proc.stdout.readline().decode()
                logs += log

                print(log, end='')

            log = proc.stdout.read().decode()
            logs += log

            print(log, end='')

            return logs


def setup_venv(venv_path, dependencies=[], debug=False):
    venv_path = str(venv_path)

    # Create virtualenv
    venv.create(venv_path, with_pip=True)

    # Install dependencies
    venv_pip('install --upgrade pip', venv_path, debug=debug)
    venv_pip('install {}'.format(' '.join(dependencies)), venv_path, debug=debug)



if __name__ == '__main__':
    setup_venv('venv', dependencies=['flask'])
    results = venv_pip('list --format=freeze --not-required', 'venv')
    print(results)
