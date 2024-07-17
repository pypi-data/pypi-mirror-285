import argparse
from dataclasses import dataclass
from .upload import upload

@dataclass
class AppContext:
    file_path: str
    group_id: str
    folder_id: str
    account_id: str
    token: str

SUB_COMMANDS = {
    "upload": upload
}

def main():
    parser = argparse.ArgumentParser(description='A simple cli tool for the sick aliyunfile')
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')
    upload_command = subparsers.add_parser('upload', help='Upload file')
    upload_command.add_argument('--file_path', type=str, help='Path of local file to upload', required=True)
    upload_command.add_argument('--folder_id', type=str, help='Target folder id, find after group from the url in browser address bar', required=True)
    upload_command.add_argument('--group_id', type=str, help='Target group id, find after group id from the url in browser address bar, or can be root', required=True)
    upload_command.add_argument('--account_id', type=str, help='Account id, find sub domain from the aliyunfile url', required=True)
    upload_command.add_argument('--token', type=str, help='Token to access aliyunfile, find access token from token in the local storage', required=True)
    args = parser.parse_args()
    if args.subcommand == 'upload':
        context = AppContext(args.file_path, args.group_id, args.folder_id, args.account_id, args.token)
        upload(context)
    else:
        raise Exception("unknown command, valid inputs: upload")
