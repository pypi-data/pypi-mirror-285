import argparse
from deploybot.commands.configure import configure
from deploybot.commands.ecs import main as ecs_main
from deploybot.commands.lambda_ import main as lambda_main
from deploybot.utils.version import get_version
import sys

VERSION = get_version()

def main():
    parser = argparse.ArgumentParser(prog='deploybot', description='Deploybot CLI')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))

    subparsers = parser.add_subparsers(dest='command')

    # Configure command
    parser_configure = subparsers.add_parser('configure', help='Configure AWS account ID and environment')
    parser_configure.set_defaults(func=configure)

    # ECS command
    parser_ecs = subparsers.add_parser('ecs', help='ECS related commands')
    parser_ecs.add_argument('action', choices=['build', 'deploy'], help='Action to perform')
    parser_ecs.add_argument('service_name', help='Name of the service')
    parser_ecs.set_defaults(func=lambda args: ecs_main([args.action, args.service_name]))

    # Lambda command
    parser_lambda = subparsers.add_parser('lambda', help='Lambda related commands')
    parser_lambda.add_argument('action', choices=['deploy'], help='Action to perform')
    parser_lambda.add_argument('service_name', help='Name of the service to deploy')
    parser_lambda.set_defaults(func=lambda args: lambda_main([args.action, args.service_name]))

    args = parser.parse_args()

    try:
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

if __name__ == '__main__':
    main()
