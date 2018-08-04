import subprocess
import paramiko
import os


DEVNULL = open(os.devnull, 'w')

def execute(commands, debug=False):
    if not debug:
        return subprocess.check_output(commands, stderr=DEVNULL).decode()
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


def remote_exec(client, command, debug=False):
    stdin, stdout, stderr = client.exec_command(command)
    if not debug:
        stdout.read().decode()
    else:
        while True:
            stdout_result = stdout.readline()
            stderr_result = stderr.readline()
            click.echo(stdout_result, nl=False)
            click.echo(stderr_result, nl=False)
            if not (stdout_result or stderr_result):    break