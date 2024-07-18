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
from datetime import datetime, timezone
from pathlib import PurePath, Path
# import requests_pkcs12
import requests
from rich import print as rprint
from rich.table import Table

from tempfile import NamedTemporaryFile

logging.basicConfig(level=logging.INFO)

HDLFSCONFIGFILE = ".hdlfscli.config.json"

blue4 = "rgb(137,209,255)"
blue7 = "rgb(0,112,242)"
info = blue4
variable = blue7

def print_file_status(files: list):
    max_len = max(len(f['pathSuffix']) for f in files)
    for f in files: 
        if f['type'] == 'DIRECTORY':
            print(f"{f['pathSuffix']:<{max_len +2}}")
        else: 
            print(f"{f['pathSuffix']:<{max_len +2}}"\
                f"{int(f['length']/1024):6} kB - {datetime.fromtimestamp(f['modificationTime'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}")

def dict2table(pdict: dict, title='Lists') -> Table:
    table = Table(title=title, header_style=variable)
    table.add_column("Key", justify="left", style=info, no_wrap=False)
    table.add_column("Value", justify="left", style=info, no_wrap=False)
    for k,v in pdict.items():
        table.add_row(str(k),str(v))
    return table

def get_path_content(response: dict) -> list:
    """
    Extracts the path items from response of LISTSTATUS API
    :param response: Response from LISTSTATUS
    :return: List of path items (folders and files)
    """
    return [f['pathSuffix'] for f in response['FileStatuses']['FileStatus']]


def get_recursive_path_content(response: dict) -> list:
    """
    Extracts the path items from response of LISTSTATUS_RECURSIVE API
    :param response: Response from LISTSTATUS_RECURSIVE
    :return: List of path items (folders and files)
    """
    page_id = response['DirectoryListing']['pageId']
    logging.info(f"Page ID: {page_id}")
    f_list = response['DirectoryListing']['partialListing']['FileStatuses']['FileStatus']
    return [f['pathSuffix'] for f in f_list]

def print_params(endpoint:str, headers:dict, params:dict, cert:str, password:str):
    rprint(dict2table({'Endpoint': endpoint, 'Headers': headers, 'Params': params, 'Cert': cert, 'Password': password}))

def hdlfs_api(method: str, operation: str) -> dict:
    """
    DECORATOR for all API-calls
    :param method: HTTP-method [get, put, ..]
    :param operation: RESTAPI name
    :return: response of Rest API
    """
    def inner_hdlfs_api(func):
        def call_api(endpoint, certificate, password, verify=True, verbose=False,**kwargs):
            container = re.match(r".+\/\/([^.]+)", endpoint).group(1)
            headers = {'x-sap-filecontainer': container}
            params = {'op': operation}
            endpoint = os.path.join(endpoint.replace('hdlfs://', 'https://'),'webhdfs/v1/')
            updated = func(endpoint, certificate, password, **kwargs)
            endpoint = endpoint + str(updated.pop('path', '').lstrip('/'))
            headers.update(updated.pop('headers', dict()))
            params.update(updated.pop('params', dict()))
            data = updated.pop('data', None)
            with requests.Session() as session:
                r = session.request(method, endpoint, cert=(certificate, password), headers=headers, params=params,
                                    data=data, verify=verify)
            # r = requests.request(method, endpoint, cert=(certificate, password), headers=headers, params=params,
            #                         data=data, verify=verify)

            if verbose:
                print_params(endpoint, headers, params, certificate, password)
            # keystore deprecated
            # suffix = PurePath(certificate).suffix
            # if suffix in ['.crt', '.pem']:
            #     r = requests.request(method, endpoint, cert=(certificate, password), headers=headers, params=params,
            #                          data=data, verify=verify)
            # elif suffix in ['.pkcs12', '.p12', '.pfx']:
            #     r = requests_pkcs12.request(method, endpoint, pkcs12_filename=certificate, pkcs12_password=password,
            #                                 headers=headers, params=params, data=data, verify=verify)

            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
            if operation not in ['OPEN','APPEND']:
                return json.loads(r.text)
            else:
                return r

        return call_api
    return inner_hdlfs_api


@hdlfs_api(method='get', operation='OPEN')
def get(endpoint: str, certificate: str, password: str, path='',
         offset=0, length=None, noredirect=False, headers={}, verify=True) \
        -> dict:
    """
    Upload file to HDFS using CREATE-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param path: path of file
    :param offset: The starting byte position
    :param length: The number of bytes to be processed.
    :param noredirect: API parameter
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    return {'path': path,
            'params': {'offset': offset, 'length': length, 'noredirect': noredirect},
            'headers': headers}


@hdlfs_api(method='put', operation='CREATE')
def upload(endpoint: str, certificate: str, password: str, destination='', data="", noredirect=False, headers={}, verify=True) \
        -> dict:
    """
    Upload file to HDFS using CREATE-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param destination: destination path of file
    :param data: file content
    :param noredirect: API parameter
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    return {'path': destination,
            'data': data,
            'params': {'noredirect': noredirect},
            'headers': {'Content-Type': 'application/octet-stream'}}


@hdlfs_api(method='put', operation='RENAME')
def rename(endpoint: str, certificate: str, password: str, path='', destination='', headers={}, verify=True) -> dict:
    """
    Rename/Move file in HDFS with RENAME-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param path: path to source file
    :param destination: destination of file
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    destination = '/' + destination if destination[0] != '/' else destination
    return {'path': path,
            'params': {'destination': destination},
            'headers': headers}


@hdlfs_api(method='put', operation='COPY')
def copy(endpoint, certificate, password, path='', destination='', a_sync=False, headers={}, verify=True):
    """
    Copy file in HDFS with Copy-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param path: path to source file
    :param destination: destination of file
    :param a_sync: API parameter
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    destination = '/' + destination if destination[0] != '/' else destination
    return {'path': path,
            'params': {'destination': destination, 'async': a_sync},
            'headers': headers}

@hdlfs_api(method='post', operation='APPEND')
def append(endpoint, certificate, password, path='', data='', a_sync=False, headers={}, verify=True):
    """
    Append data to file in HDFS with Copy-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param path: path to source file
    :param destination: destination of file
    :param a_sync: API parameter
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    return {'path': path,
            'data': data,
            'params': {'async': a_sync},
            'headers': {'Content-Type': 'application/octet-stream'}}


@hdlfs_api(method='DELETE', operation='DELETE')
def delete(endpoint: str, certificate: str, password: str, path='', headers={}, verify=True) -> dict:
    """
    Delete file in HDFS with DELETE-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param path: path to source file
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    headers.update({'Content-Type': 'application/json'})
    return {'path': path,
            'headers': headers,
            'snapshotname': datetime.now(timezone.utc)}


@hdlfs_api(method='get', operation='GETFILESTATUS')
def file_status(endpoint: str, certificate: str, password: str, path='', headers={}, verify=True):
    """
    Get file status
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param path: path to source file
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    headers.update({'Content-Type': 'application/json'})
    return {'path': path,
            'headers': headers}


@hdlfs_api(method='get', operation='LISTSTATUS')
def list_path(endpoint: str, certificate: str, password: str, path='', headers={}, verify=True):
    """
    Get all items of folder by using LISTSTATUS-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param path: path to source file
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    headers.update({'Content-Type': 'application/json'})
    return {'path': path,
            'headers': headers}


@hdlfs_api(method='get', operation='LISTSTATUS_RECURSIVE')
def list_path_recursive(endpoint: str, certificate: str, password: str, path='', start_after=None, headers={},
                        verify=True) -> dict:
    """
    Get all items of folder and sub-folders by using LISTSTATUS_RECURSIVE-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param path: path to source file
    :param start_after: API parameter for paging result
    :param headers: Passing optional parameter to API
    :param verify: Enables/ disables server verification
    :return: response
    """
    headers.update({'Content-Type': 'application/json'})
    return {'path': path,
            'params': {'startAfter': start_after},
            'headers': headers}


@hdlfs_api(method='get', operation='WHOAMI')
def whoami(endpoint: str, certificate: str, password: str, verify=True):
    """
    Get user information by WHOAMI-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param verify: Enables/ disables server verification
    :return: response
    """
    return {'headers': {'Content-Type': 'application/json'}}


# UNTESTED
@hdlfs_api(method='get', operation='GETOPERATIONSTATUS')
def get_operations_status(endpoint: str, certificate: str, password: str, token='',verify=True) -> dict:
    """
    Get operation status by GETOPERATIONSTATUS-API
    :param endpoint: endpoint url
    :param certificate: filename with path to certificate or pkcs12-keystore
    :param password: filename with path to key or passphrase for keystore
    :param verify: Enables/ disables server verification
    :return: response
    """
    return {'params': {'token': token},
            'headers': {'Content-Type': 'application/json'}}

# UNTESTED
@hdlfs_api(method='get', operation='GETRESTORESNAPSHOTSTATUS')
def get_operations_status(endpoint, certificate, password, token='', verify=True):
    return {'params': {'token': token},
            'headers': {'Content-Type': 'application/json'}}


def read_config(config: str):
    hdlfs_config_file = Path.home() / HDLFSCONFIGFILE 
    logging.debug(f"Using HDLFS config: {config} in {hdlfs_config_file}")
    with open(hdlfs_config_file,"r") as fp:
        params = json.load(fp)["configs"][config]
    return params


class HDLFSConnect:
    def __init__(self,cert_file:str, key_file:str, endpoint:str):
        self.cert_file = cert_file
        self.key_file = key_file
        self._verbose = False
        self._verify = True
        self._no_redirect = False
        container = re.match(r'.+\/\/([^.]+)', endpoint).group(1)
        self.headers = {'x-sap-filecontainer': container, 'Content-Type': 'application/json'}
        self.endpoint = os.path.join(endpoint.replace('hdlfs://', 'https://'),'webhdfs/v1/')
        self.params =  {'noreadirect': self._no_redirect}

    def set_verbose(self, verbose: bool):
        self._verbose = verbose
    
    def set_verify(self, verify: bool):
        self._verify = verify

    def set_no_redirect(self, no_redirect: bool):
        self._no_redirect = no_redirect

    def set_with_temp_files(self, certificate: str, key: str):
        with NamedTemporaryFile(mode='w+b',delete=False) as self.cert_file, NamedTemporaryFile(mode='w+b',delete=False) as self.key_file:
            self.cert_file.write(certificate.encode('utf-8')); self.cert_file.seek(0)
            self.key_file.write(key.encode('utf-8'));  self.key_file.seek(0)

    def upload(self, path: str, data: str):
        with requests.Session() as session:
            params = self.params.copy()
            params['op']='CREATE'
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            headers['Content-Type'] = 'application/octet-stream'
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('PUT', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
        return json.loads(r.text)
    
    def append(self, path: str, data: str):
        with requests.Session() as session:
            params = self.params.copy()
            params['op'] = 'APPEND'
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            headers['Content-Type'] = 'application/octet-stream'
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('POST', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
        return r
    
    def download(self, path: str, length=None, offset=0) -> dict:
        with requests.Session() as session:
            params = self.params.copy()
            params['op'] = 'OPEN'
            params['offset'] = offset
            params['length'] = length
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('GET', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
        return r.text
    
    def list(self, path: str):
        with requests.Session() as session:
            params = self.params.copy()
            params['op'] = 'LISTSTATUS'
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('GET', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
        return json.loads(r.text)['FileStatuses']['FileStatus']
    
    def listr(self, path: str,start_after=None):
        with requests.Session() as session:
            params = self.params.copy()
            params['op'] = 'LISTSTATUS_RECURSIVE'
            params['startAfter'] = start_after
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('GET', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
        return json.loads(r.text)['DirectoryListing']['partialListing']['FileStatuses']['FileStatus']
    
    def delete(self, path: str) -> list:
        if self.file_status(path)['type'] == 'FILE':
            return [self.delete_file(path=path)]
        else:
            files = self.listr(path)
            return self.delete_files(path, files)
   

    def delete_file(self, path: str) -> list:
        with requests.Session() as session:
            params = self.params.copy()
            params['op']='DELETE'
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('DELETE', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
            response = json.loads(r.text)
            response['file'] = path
            return response
    
    def delete_files(self, parent_folder: str, paths: list) -> list:
        responses = []
        with requests.Session() as session:
            params = self.params.copy()
            params['op']='DELETE'
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            if self._verbose:
                print("Deleting files RestAPI call - endpoints + path")
                print_params(self.endpoint + paths[0]['pathSuffix'], headers, params, self.cert_file, self.key_file)
            for f in paths:
                endpoint = self.endpoint + os.path.join(parent_folder,f['pathSuffix'])
                r = session.request('DELETE', endpoint, params=params, verify=self._verify)
                if r.status_code not in [200, 201]:
                    raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
                response = json.loads(r.text)
                response['file'] = os.path.join(parent_folder,f['pathSuffix'])
                responses.append(response)
            return responses
    
    def rename(self, path: str, destination: str):
        with requests.Session() as session:
            params = self.params.copy()
            params['op']='RENAME'
            params['destination'] = destination
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('PUT', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
        return json.loads(r.text)

    def copy(self, path: str, destination: str, a_sync=False):
        with requests.Session() as session:
            params = self.params.copy()
            params['op']='COPY'
            params['destination'] = destination
            params['async'] = a_sync
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('PUT', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
        return json.loads(r.text)
    
    def file_status(self, path: str):   
        with requests.Session() as session:
            params = self.params.copy()
            params['op']='GETFILESTATUS'
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            endpoint = self.endpoint + path
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('GET', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
            return json.loads(r.text)['FileStatus']
    
    def whoami(self):
        with requests.Session() as session:
            params = self.params.copy()
            params['op']='WHOAMI'
            session.cert = (self.cert_file, self.key_file)
            headers = self.headers.copy()
            session.headers.update(headers)
            endpoint = self.endpoint
            if self._verbose:
                print_params(endpoint, headers, params, self.cert_file, self.key_file)
            r = session.request('GET', endpoint, params=params, verify=self._verify)
            if r.status_code not in [200, 201]:
                raise ValueError(f"Unsuccessful API-call - Status code: {r.status_code} - {r.text}")
            return json.loads(r.text)
    
    def print_content(self, path: str):
        files = self.list(path)
        print_file_status(files)

    def list_content(self, path: str, filter=None):
        files = self.list(path)
        if not filter:
            return [ f['pathSuffix'] for f in files]
        else: 
            return [ f['pathSuffix'] for f in files if f['type'] == filter]
    
    def file_exists(self, path: str):    
        try:
            response = self.file_status(path)
            return True
        except:
            return False
        
    def print(self):
        print(f"Endpoint: {self.endpoint}")
        print(f"Container: {self.container}")
        print(f"Cert: {self.cert_file}")
        print(f"Key: {self.key_file}")
        print(f"Verbose: {self.verbose}")

    # def close(self,):
    #     os.unlink(self.cert_file.name)
    #     os.unlink(self.key_file.name)
    
def main():
    parser = argparse.ArgumentParser("Work with filesystem HDLFS")
    parser.add_argument("command", choices=['upload','filestatus', 'append', 'download', 'list', 'listr','delete', 'rename', 'copy', 'exists','whoami'],
                        help="Actions: upload, download, list, delete, rename, copy")
    parser.add_argument("path", nargs='?', help="Path to file for uploading or path on HDLFS to download")
    parser.add_argument("target", nargs='?', help="For downloading the target path  ")
    parser.add_argument("-c", "--config", help="HDLFS config", default="default")
    parser.add_argument("-n", "--num_bytes", help="Number of bytes to download", type=int, default=None)

    args = parser.parse_args()
    params = read_config(args.config)
    hdlconnect = HDLFSConnect(params['cert'], params['key'], params['endpoint'])
    hdlconnect.set_verbose(True)

    # with open(params['cert'], 'r') as file:
    #     cert = file.read()
    # with open(params['key'], 'r') as file:
    #     key = file.read()
    
    match args.command:
        case 'upload':
            print(f"Uploading: {args.path} -> {args.target}")
            with open(args.path, 'r') as file:
                data = file.read()
            response = hdlconnect.upload(path=args.target, data=data)
            print(f"Uploaded: {response['Location']}")
        case 'append':
            print(f"Append to {args.path}")
            response = hdlconnect.append(path=args.path, data=args.target)
            print(f"Appended: {response}")
        case 'rename':
            print(f"Rename {args.path} ->{args.target}")
            target = args.target if args.target.startswith('/') else '/' + args.target
            response = hdlconnect.rename(path=args.path, destination=target)
            print(f"Renamed: {response}")
        case 'copy':
            print(f"Copy {args.path} ->{args.target}")
            target = args.target if args.target.startswith('/') else '/' + args.target
            response = hdlconnect.rename(path=args.path, destination=target)
            print(f"Copied: {response}")
        case 'download':
            if args.target:
                print(f"Downloading: {args.path} -> {args.target}")
            else: 
                print(f"Downloading: {args.path}")
            if args.num_bytes:
                print(f"Number of bytes to download: {args.num_bytes}")
                num_bytes = int(args.num_bytes)
            else: 
                num_bytes = None
            data = hdlconnect.download(path=args.path, length=num_bytes)
            if args.target:
                with open(args.target, 'w') as file:
                    file.write(data)
            else: 
                print(data)
        case 'list':
            folder = args.path if args.path  else '/'
            print(f"Listing files of folder: {folder}")
            files = hdlconnect.print_content(path=folder)
            # print(hdlconnect.list_content(folder, 'DIRECTORY'))
        case 'listr':
            folder = args.path if args.path  else '/'
            print(f"Listing files of folder: {folder}")
            files = hdlconnect.listr(path=folder)
            print_file_status(files)
        case 'filestatus':
            result = hdlconnect.file_status(args.path)
            print(f"File exists: {result}")
        case 'exists':
            result = hdlconnect.file_exists(args.path)
            print(f"File exists: {result}")
        case 'delete':
            result = hdlconnect.delete(args.path)
            print(f"Delete: {result}")
        case 'whoami':
            result = hdlconnect.whoami()
            print(f"Who am I: {result}")

if __name__ == '__main__':
    main() 