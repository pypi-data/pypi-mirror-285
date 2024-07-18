import subprocess

def get_aws_account_id():
    result = subprocess.run(
        ['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise RuntimeError("Failed to get AWS account ID: {}".format(result.stderr.decode('utf-8')))
    return result.stdout.decode('utf-8').strip()
