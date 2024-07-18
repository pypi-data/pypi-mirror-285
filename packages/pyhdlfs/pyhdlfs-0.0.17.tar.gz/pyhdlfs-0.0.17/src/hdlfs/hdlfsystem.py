"""
Python interface to SAP HDLFS.

Status: Work in progress, unsupported

by Thorsten Hapke, thorsten.hapke@sap.com
"""

import json
import logging
from datetime import datetime
from pathlib import PurePath, Path
from rich import print as rprint
from rich.table import Table

import pyarrow.fs as pafs
from pyarrow import NativeFile, fs
import hdlfs

logging.basicConfig(level=logging.INFO)

HDLFSCONFIGFILE = ".hdlfscli.config.json"

blue4 = "rgb(137,209,255)"
blue7 = "rgb(0,112,242)"

info = blue4
variable = blue7

class hldfsNativeFile(NativeFile):

    def __init__(self,config: str, root_path):
        """
        Init NativeFile by reading the config of file <.hdlfscli.config.json>
        :param config: config params of .hdlfscli.config.json
        :return: None
        """
        with open(Path.home() / HDLFSCONFIGFILE) as fp:
            params = json.load(fp)["configs"][config]
        self.config = config
        self.endpoint = params['endpoint']
        self.certificate = params['cert']
        self.key = params['key']
        self.timeout = params['timeout']
        self.format = params['format']
        self.root_path = root_path
        self.path = '/'


    def write(self, data):
        hdlfs.upload(self.endpoint, self.certificate, self.key, 
                     destination=self.path, data=data, noredirect=False, headers={}, verify=True) 
        return None


    def print_conf(self) -> None:
        print('\n')
        table = Table(title=f"Configuration File: {Path.home() / HDLFSCONFIGFILE}", header_style=variable)
        table.add_column("Config", justify="left", style=info, no_wrap=False)
        table.add_column("Value", justify="left", style=info, no_wrap=False)
        table.add_row('endpoint',self.endpoint)
        table.add_row('certificate',self.certificate)
        table.add_row('key-file',self.key)
        rprint(table)


class HDLFileSystem(fs.FileSystem):

    def __init__(self,config: str, root_path='/n'):
        self.hdlfs = hldfsNativeFile(config, root_path=root_path)

    def print_conf(self) -> None:
        self.hdlfs.print_conf()


    def type_name(self):
        return "hdlfs"

    def root_uri(self):
        return self.root_path
    
    def open_output_stream(self, path, compression='detect', buffer_size=None, metadata=None):
        self.hdlfs.path = path
        return self.hdlfs

def main():
    hdlfs = HDLFileSystem("canaryds")
    hdlfs.print_conf()
    rprint(hdlfs.type_name())

    with hdlfs.open_output_stream('data/hello.txt') as stream:
        stream.write(b"Hello, World")


if __name__ == '__main__':
    main()

