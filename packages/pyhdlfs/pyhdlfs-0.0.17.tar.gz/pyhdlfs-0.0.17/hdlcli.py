
import json
import logging
import argparse
from pathlib import  Path

from rich import print as rprint
from rich.table import Table

from hdlfs.hdlfs import *

logging.basicConfig(level=logging.INFO)

HDLFSCONFIGFILE = ".hdlfscli.config.json"

blue4 = "rgb(137,209,255)"
blue7 = "rgb(0,112,242)"
info = blue4
variable = blue7

def main():
    parser = argparse.ArgumentParser("Work with filesystem HDLFS")
    parser.add_argument("command", choices=['upload','upload', 'download', 'list', 'listr','delete', 'rename', 'copy'],
                        help="Actions: upload, download, list, delete, rename, copy")
    parser.add_argument("path", nargs='?', help="Path to file for uploading or path on HDLFS to download")
    parser.add_argument("target", nargs='?', help="For downloading the target path  ")
    parser.add_argument("-c", "--config", help="HDLFS config", default="default")

    args = parser.parse_args()

    params = read_config(args.config)

    match args.command:
        case 'upload':
            print(f"Uploading: {args.path} -> {args.target}")
            with open(args.path, 'r') as file:
                data = file.read()
            response = upload(endpoint=params['endpoint'], certificate=params['cert'], password=params['key'], destination=args.target, data=data)
            print(f"Uploaded: {response['Location']}")
        case 'download':
            if args.target:
                print(f"Downloading: {args.path} -> {args.target}")
            else: 
                print(f"Downloading: {args.path}")
            response = get(endpoint=params['endpoint'], certificate=params['cert'], password=params['key'], path=args.path)
            if args.target:
                with open(args.target, 'w') as file:
                    file.write(response.text)
            else: 
                print(response.text)
        case 'list':
            folder = args.path if args.path  else '/'
            print(f"Listing files of folder: {folder}")
            files = list_path(endpoint=params['endpoint'], certificate=params['cert'], password=params['key'], path=folder)['FileStatuses']['FileStatus']
            print_file_status(files)
        case 'listr':
            folder = args.path if args.path  else '/'
            print(f"Listing files of folder: {folder}")
            files = list_path_recursive(endpoint=params['endpoint'], certificate=params['cert'], password=params['key'], path=folder)['DirectoryListing']['partialListing']['FileStatuses']['FileStatus'] 
            print_file_status(files)
        case 'delete':
            print(f"Deleting: {args.path} ")
            response = delete(endpoint=params['endpoint'], certificate=params['cert'], password=params['key'], path=args.path)
            print(f"Successful: {response['boolean']}")
        case 'rename':
            print(f"Renaming: {args.path} ")
            response = rename(endpoint=params['endpoint'], certificate=params['cert'], password=params['key'], path=args.path, destination=args.target)
            print(f"Successful: {response['boolean']}")
        case 'copy':
            print(f"Copying: {args.path} -> {args.target} ")
            response = copy(endpoint=params['endpoint'], certificate=params['cert'], password=params['key'], path=args.path, destination=args.target)
            print(f"Successful: {response['boolean']}")
        case _:
            print("Unknown command")

if __name__ == '__main__':
    main()