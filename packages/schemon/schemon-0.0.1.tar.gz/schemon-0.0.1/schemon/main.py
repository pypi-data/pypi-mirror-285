import sys
import os
import argparse
from schemon.publish import publish_cli
from schemon.validate import validate_cli, ValidationResultItemStatusEnum


def validate_directory(directory):
    if os.path.isdir(directory):
        return
    else:
        print(f"Error: {directory} is not a valid directory")


def validate_file(file):
    if os.path.isfile(file):
        return
    else:
        print(f"Error: {file} is not a valid file")


def list_all_yaml_files_in_dir(directory):
    """
    Returns a list of all YAML files in the specified directory and its subdirectories.

    Args:
        directory (str): The directory to search for YAML files.

    Returns:
        list: A list of file paths for all YAML files found.
    """
    yaml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".yaml"):
                yaml_files.append(os.path.join(root, file))
    return yaml_files


def main():
    """
    Entry point of the schemon command line tool.

    This function parses the command line arguments, validates the input, and performs the specified command.
    The command can be either "validate" or "publish". The input can be a YAML directory or file.
    """

    parser = argparse.ArgumentParser(description="schemon command line tool")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    parser_validate = subparsers.add_parser(
        "validate", help="Validate a directory or file"
    )

    validate_group = parser_validate.add_mutually_exclusive_group(required=True)
    validate_group.add_argument(
        "-d", "--directory", type=str, help="The directory to validate"
    )
    validate_group.add_argument("-f", "--file", type=str, help="The file to validate")
    parser_validate.add_argument(
        "-n",
        "--notification",
        type=str,
        choices=["console", "pr"],
        help='Notification argument (must be "console" or "pr")',
    )
    parser_validate.add_argument(
        "-p", "--platform", type=str, help="Platform for PR notification"
    )
    parser_validate.add_argument(
        "-i", "--pr_id", type=str, help="PR ID for notification"
    )
    parser_validate.add_argument(
        "-r", "--repo", type=str, help="Repository for PR notification"
    )

    parser_publish = subparsers.add_parser(
        "publish", help="Publish the directory or file after validation"
    )
    publish_group = parser_publish.add_mutually_exclusive_group(required=True)
    publish_group.add_argument(
        "-d", "--directory", type=str, help="The directory to publish"
    )
    publish_group.add_argument("-f", "--file", type=str, help="The file to publish")

    if len(sys.argv) < 3:
        parser.print_help(sys.stderr)
        sys.exit(0)

    args = parser.parse_args()

    files = []

    if args.command == "validate":
        notification = args.notification
        if notification == "pr" and not all([args.platform, args.pr_id, args.repo]):
            parser_validate.error(
                "The arguments -p/--platform, -i/--pr_id, and -r/--repo are required when -n/--notification is 'pr'"
            )
        if args.directory:
            validate_directory(args.directory)
            files = list_all_yaml_files_in_dir(args.directory)
        elif args.file:
            validate_file(args.file)
            files = [args.file]
        if notification == "pr":
            ret = validate_cli(
                files,
                notification,
                platform=args.platform,
                pr_id=args.pr_id,
                repo_id=args.repo,
            )
        else:
            ret = validate_cli(files, notification)
    elif args.command == "publish":
        if args.directory:
            validate_directory(args.directory)
            files = list_all_yaml_files_in_dir(args.directory)
        elif args.file:
            validate_file(args.file)
            files = [args.file]
        ret = publish_cli(files)
    else:
        parser.print_help(sys.stderr)
        ret = ValidationResultItemStatusEnum.INVALID
    sys.exit(ret)


if __name__ == "__main__":
    main()
