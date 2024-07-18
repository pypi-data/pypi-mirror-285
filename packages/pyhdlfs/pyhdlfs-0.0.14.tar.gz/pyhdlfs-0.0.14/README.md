# PyHDLFS

PythonAPI for SAP HDLFS using the [RestAPI](https://help.sap.com/doc/9d084a41830f46d6904fd4c23cd4bbfa/2023_1_QRC/en-US/html/index.html)

For authentication both options are supported: key/certification and keystore/passphrase. The suffix of the certification 
file is used for selecting the authentication method. 

- Certification: .crt or .pem
- Keystore: .pkcs12, .p12 or .pfx

Status: In Progress, unsupported

[Generated Documentation](hdlfs_doc.md) 

# Table of Contents

* [hdlfs](#hdlfs)
  * [get\_path\_content](#hdlfs.get_path_content)
  * [get\_recursive\_path\_content](#hdlfs.get_recursive_path_content)
  * [hdlfs\_api](#hdlfs.hdlfs_api)
  * [upload](#hdlfs.upload)
  * [rename](#hdlfs.rename)
  * [copy](#hdlfs.copy)
  * [delete](#hdlfs.delete)
  * [file\_status](#hdlfs.file_status)
  * [list\_path](#hdlfs.list_path)
  * [list\_path\_recursive](#hdlfs.list_path_recursive)
  * [whoami](#hdlfs.whoami)
  * [get\_operations\_status](#hdlfs.get_operations_status)


<a id="hdlfs"></a>

# hdlfs

<a id="hdlfs.get_path_content"></a>

#### get\_path\_content

```python
def get_path_content(response: dict) -> list
```

Extracts the path items from response of LISTSTATUS API

**Arguments**:

- `response`: Response from LISTSTATUS

**Returns**:

List of path items (folders and files)

<a id="hdlfs.get_recursive_path_content"></a>

#### get\_recursive\_path\_content

```python
def get_recursive_path_content(response: dict) -> list
```

Extracts the path items from response of LISTSTATUS_RECURSIVE API

**Arguments**:

- `response`: Response from LISTSTATUS_RECURSIVE

**Returns**:

List of path items (folders and files)

<a id="hdlfs.hdlfs_api"></a>

#### hdlfs\_api

```python
def hdlfs_api(method: str, operation: str) -> dict
```

DECORATOR for all API-calls

**Arguments**:

- `method`: HTTP-method [get, put, ..]
- `operation`: RESTAPI name

**Returns**:

response of Rest API

<a id="hdlfs.upload"></a>

#### upload

```python
@hdlfs_api(method='put', operation='CREATE')
def upload(endpoint: str,
           certificate: str,
           password: str,
           destination='',
           data="",
           noredirect=False,
           headers={},
           verify=True) -> dict
```

Upload file to HDFS using CREATE-API

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `destination`: destination path of file
- `data`: file content
- `noredirect`: API parameter
- `headers`: Passing optional parameter to API
- `verify`: Enables/ disables server verification

**Returns**:

response

<a id="hdlfs.rename"></a>

#### rename

```python
@hdlfs_api(method='put', operation='RENAME')
def rename(endpoint: str,
           certificate: str,
           password: str,
           path='',
           destination='',
           headers={},
           verify=True) -> dict
```

Rename/Move file in HDFS with RENAME-API

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `path`: path to source file
- `destination`: destination of file
- `headers`: Passing optional parameter to API
- `verify`: Enables/ disables server verification

**Returns**:

response

<a id="hdlfs.copy"></a>

#### copy

```python
@hdlfs_api(method='put', operation='COPY')
def copy(endpoint,
         certificate,
         password,
         path='',
         destination='',
         a_sync=False,
         headers={},
         verify=True)
```

Copy file in HDFS with Copy-API

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `path`: path to source file
- `destination`: destination of file
- `a_sync`: API parameter
- `headers`: Passing optional parameter to API
- `verify`: Enables/ disables server verification

**Returns**:

response

<a id="hdlfs.delete"></a>

#### delete

```python
@hdlfs_api(method='del', operation='DELETE')
def delete(endpoint: str,
           certificate: str,
           password: str,
           path='',
           headers={},
           verify=True) -> dict
```

Delete file in HDFS with DELETE-API

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `path`: path to source file
- `headers`: Passing optional parameter to API
- `verify`: Enables/ disables server verification

**Returns**:

response

<a id="hdlfs.file_status"></a>

#### file\_status

```python
@hdlfs_api(method='get', operation='GETFILESTATUS')
def file_status(endpoint: str,
                certificate: str,
                password: str,
                path='',
                headers={},
                verify=True)
```

Get file status

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `path`: path to source file
- `headers`: Passing optional parameter to API
- `verify`: Enables/ disables server verification

**Returns**:

response

<a id="hdlfs.list_path"></a>

#### list\_path

```python
@hdlfs_api(method='get', operation='LISTSTATUS')
def list_path(endpoint: str,
              certificate: str,
              password: str,
              path='',
              headers={},
              verify=True)
```

Get all items of folder by using LISTSTATUS-API

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `path`: path to source file
- `headers`: Passing optional parameter to API
- `verify`: Enables/ disables server verification

**Returns**:

response

<a id="hdlfs.list_path_recursive"></a>

#### list\_path\_recursive

```python
@hdlfs_api(method='get', operation='LISTSTATUS_RECURSIVE')
def list_path_recursive(endpoint: str,
                        certificate: str,
                        password: str,
                        path='',
                        start_after=None,
                        headers={},
                        verify=True) -> dict
```

Get all items of folder and sub-folders by using LISTSTATUS_RECURSIVE-API

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `path`: path to source file
- `start_after`: API parameter for paging result
- `headers`: Passing optional parameter to API
- `verify`: Enables/ disables server verification

**Returns**:

response

<a id="hdlfs.whoami"></a>

#### whoami

```python
@hdlfs_api(method='get', operation='WHOAMI')
def whoami(endpoint: str, certificate: str, password: str, verify=True)
```

Get user information by WHOAMI-API

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `verify`: Enables/ disables server verification

**Returns**:

response

<a id="hdlfs.get_operations_status"></a>

#### get\_operations\_status

```python
@hdlfs_api(method='get', operation='GETOPERATIONSTATUS')
def get_operations_status(endpoint: str,
                          certificate: str,
                          password: str,
                          token='',
                          verify=True) -> dict
```

Get operation status by GETOPERATIONSTATUS-API

**Arguments**:

- `endpoint`: endpoint url
- `certificate`: filename with path to certificate or pkcs12-keystore
- `password`: filename with path to key or passphrase for keystore
- `verify`: Enables/ disables server verification

**Returns**:

response

