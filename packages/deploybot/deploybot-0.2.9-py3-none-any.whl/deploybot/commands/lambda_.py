import argparse
from deploybot.commands.shared import deploy
import sys

def lambda_(args):
    """Deploy Lambda services.

    ACTION: Action to perform (deploy).
    SERVICE_NAME: Name of the service to deploy.
    """
    deploy('lambda', args.action, args.service_name)

def main(args=None):
    parser = argparse.ArgumentParser(description='Deploy Lambda services')
    parser.add_argument('action', choices=['deploy'], help='Action to perform (deploy)')
    parser.add_argument('service_name', help='Name of the service to deploy')
    
    if args is None:
        args = []

    try:
        parsed_args = parser.parse_args(args)
        lambda_(parsed_args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

if __name__ == '__main__':
    main()
