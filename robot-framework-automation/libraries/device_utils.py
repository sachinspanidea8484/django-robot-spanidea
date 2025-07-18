import json
from SSHLibrary import SSHLibrary


def load_device_config(path):
    with open(path) as f:
        return json.load(f)


def run_command_and_get_output(ip, user, password, command):
    ssh = SSHLibrary()
    ssh.open_connection(ip)
    ssh.login(user, password)
    output = ssh.execute_command(command)
    ssh.close_connection()
    return output
