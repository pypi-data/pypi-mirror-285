"""
Python interface to SAP HDLFS.

Status: Work in progress, unsupported

by Thorsten Hapke, thorsten.hapke@sap.com
"""

import json
import re
import os
import logging
import argparse
import sys
from datetime import datetime, timezone
from pathlib import PurePath, Path
sys.path.append(str(Path(__file__).parent))


import requests
from rich import print as rprint
from rich.table import Table

from hdlfs import HDLFSConnect, read_config


def main():
    parser = argparse.ArgumentParser("Copy between HDLFS")
    parser.add_argument("source_hdlfs", help="config source HDLFS")
    parser.add_argument("source_path", help="source path")
    parser.add_argument("target_hdlfs",help="config target HDLFS")
    parser.add_argument("target_path", help="HDLFS config")

    args = parser.parse_args()
    source_params = read_config(args.source_hdlfs)
    hdl_source = HDLFSConnect(source_params['cert'], source_params['key'], source_params['endpoint'])

    target_params = read_config(args.source_hdlfs)
    hdl_target = HDLFSConnect(target_params['cert'], target_params['key'], target_params['endpoint'])

    source_path = args.source_path[1:] if args.source_path.startswith('/')  else  args.source_path
    target_path = args.target_path[1:] if args.target_path.startswith('/')  else  args.target_path

if __name__ == '__main__':
    main() 