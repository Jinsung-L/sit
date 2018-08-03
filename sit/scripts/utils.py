import subprocess

def execute(commands, debug=False):
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
