#####
#Author: LordCasser
# Date: 2020-03-26 12:31:53
#LastEditTime: 2020-03-27 19:41:38
#LastEditors: LordCasser
# Description:
#####
from lib.utils import _mkdir, _print, getFile
import os
import re
from lib import dsstore
import sys


class DSStoreHack(object):
    def __init__(self, ds_path):
        if os.path.exists(ds_path):
            self.ds_path = ds_path
            self.local = True
        elif (ds_path.startswith('http')
                and ds_path.endswith('/')):
            self.ds_path = re.search(r'https?://(.*)',
                                     ds_path).group(1).replace(':', '_')
            # _mkdir(self.ds_path)
            self.local = False
        else:
            _print("[-] Please enter right DS_Store file path", "red")
            _print("\t[example] Local: ", 'green')
            _print("\t[example] remote: 'http://example.com/.DS_Store/'", 'green')

    def _parse_file(self):
        file = getFile(self.ds_path, self.local)
        ds = dsstore.DS_Store(file, debug=False)
        files = ds.traverse_root()
        _print("[+]File count: "+ str(len(files)))
        for i in files:
            _print("[+] " + i)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        _print("[*] USAGE: python3 Ds_StoreHack.py <local_path>|<remote_url>")
        _print("\t[example] Local: python3 Ds_StoreHack.py ./DS_Store ", 'green')
        _print(
            "\t[example] remote:  python3 Ds_StoreHack.py 'http://example.com/.DS_Store/'", 'green')
        exit()
    if len(sys.argv) == 2:
        DS = DSStoreHack(sys.argv[1])
        DS._parse_file()
