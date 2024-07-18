import argparse
from deploybot.commands.shared import deploy
import sys

def ecs(args):
    """Deploy ECS services.

    ACTION: Action to perform (build or deploy).
    SERVICE_NAME: Name of the service to deploy.
    """
    deploy('ecs', args.action, args.service_name)

def main(args=None):
    parser = argparse.ArgumentParser(description='Deploy ECS services')
    parser.add_argument('action', choices=['build', 'deploy'], help='Action to perform (build or deploy)')
    parser.add_argument('service_name', help='Name of the service to deploy')
    
    if args is None:
        args = []

    try:
        parsed_args = parser.parse_args(args)
        ecs(parsed_args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

if __name__ == '__main__':
    main()
