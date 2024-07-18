
import json
from yaml import dotenv_values

from hdlfs.hdlfs import *

# Credentials
passphrase = dotenv_values('.env')['keystore_pwd']
keystore = "config/keystore.p12"

cert = '/Users/d051079/certs/thh.crt'
key = '/Users/d051079/certs/thh.key'

WITH_PKCS = False
if WITH_PKCS:
    print("With Keystore")
    key = passphrase
    cert = keystore
else:
    print("With Certificate")

connections_file = "config/connections.json"

with open(connections_file) as js:
    connections = json.load(js)
connections = connections["CoolR"]
url = connections['bronze']['endpoint']

connections_file = "config/connections.json"


# r = list_files(url, path=path, password=key, certificate=cert, verify=False)
#
# for f in r['FileStatuses']['FileStatus']:
#     print(f"{f['pathSuffix']} - {f['type']}")

filenr = 12
file1 = f'/testdata/sub1/file{filenr}.txt'
r = upload(url, data='This is a test-file', destination=file1, password=key, certificate=cert, verify=False)
print(f"Upload {file1}: {r}")

file2 = f'/testdata/file{filenr}.txt'
r = rename(url, path=file1, destination=file2, password=key, certificate=cert, verify=False)
print(f"Renaming {file1} -> {file2}: {r}")

file3 = f'/testdata/file{filenr}-copy.txt'
r = copy(url, path=file2, destination=file3, password=key, certificate=cert, verify=False)
print(f"Copy {file2} -> {file3}: {r}")

path = 'testdata'
r = list_path(url, path=path, password=key, certificate=cert, verify=False)
print(f"List Folder {path}: {get_path_content(r)}")

path_sub1 = 'testdata/sub1'
r = list_path(url, path=path_sub1, password=key, certificate=cert, verify=False)
print(f"List Folder {path_sub1}: {get_path_content(r)}")

r = file_status(url, path=file3, password=key, certificate=cert, verify=False)
print(f"File Status {file3}: {r}")

path = 'testdata'
r = list_path_recursive(url, path=path, password=key, certificate=cert, start_after=None, verify=False)
print(f"List Recursive Folder {path}: {get_recursive_path_content(r)}")
# ic(r)

r = whoami(url, password=key, certificate=cert, verify=False)
print(f"Whoami: {r}")

# r = delete(url, path=file2, password=key, certificate=cert, verify=False)
# print(f"After \'Delete\' {file2} List Folder {path}: {get_files(r)}")

import unittest
from hdlfs import hdlfs  # Adjust the import based on the actual package structure

class TestHDLFS(unittest.TestCase):
    def setUp(self):
        # Setup code here (if needed)
        pass

    def test_function1(self):
        # Example test for a hypothetical function1
        # result = hdlfs.function1(args)
        # self.assertEqual(result, expected_result)
        pass

    def test_function2(self):
        # Example test for a hypothetical function2
        # result = hdlfs.function2(args)
        # self.assertTrue(result)
        pass

    # Additional test methods for other functions

if __name__ == '__main__':
    unittest.main()