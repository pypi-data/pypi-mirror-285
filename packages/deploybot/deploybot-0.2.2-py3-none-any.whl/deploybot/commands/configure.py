import subprocess
import os
from deploybot.utils.aws import get_aws_account_id
from deploybot.utils.config import save_config

def configure(args):
    """Configure AWS account ID and set the environment."""
    aws_account_id = input('Enter your AWS account ID: ')
    actual_aws_account_id = get_aws_account_id()

    if actual_aws_account_id != aws_account_id:
        print("AWS account ID does not match the current AWS CLI configuration.")
        return

    while True:
        environment = input("Select environment (staging/production): ").strip().lower()
        if environment in ["staging", "production"]:
            break
        print("Invalid choice. Please select either 'staging' or 'production'.")

    base_path = input('Enter the base path of the project: ')

    os.chdir(base_path)
    branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()

    if environment == 'staging' and branch == 'master':
        print("Warning: Selected staging environment but the branch is master.")
        return
    elif environment == 'production' and branch != 'master':
        print("Warning: Selected production environment but the branch is not master.")
        return

    print("You added this account ID: {}".format(aws_account_id))
    print("This is the environment: {}".format(environment))
    print("This is the path: {}".format(base_path))
    print("This is the branch: {}".format(branch))

    confirm = input("Are you sure to save these settings? (yes/no): ").strip().lower()
    if confirm == 'yes':
        save_config(aws_account_id, environment, base_path, branch)
        os.environ['ENVIRONMENT'] = environment
        os.environ['AWS_ACCOUNT_ID'] = aws_account_id
        print("Configuration saved: AWS account ID = {}, Environment = {}, Base Path = {}, Branch = {}".format(aws_account_id, environment, base_path, branch))

def main(args=None):
    configure(args)

if __name__ == '__main__':
    main()
