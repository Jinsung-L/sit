import subprocess
import paramiko

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


def connect_ssh(address, username, password):
    # Make SSH connection
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(address, username=username, password=password)
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        raise e

    return client
