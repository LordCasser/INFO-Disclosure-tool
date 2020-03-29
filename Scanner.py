#####
#Author: LordCasser
# Date: 2020-03-27 20:44:31
#LastEditTime: 2020-03-27 21:40:39
#LastEditors: LordCasser
# Description:
#####
import ssl
from urllib import request
from lib.utils import _mkdir, _print


class Scanner(object):
    def __init__(self, url: str):
        self.info = []
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        elif not url.endswith("/"):
            url = url + "/"
        self.url = url

    def _scan(self, url, download=False):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        resp = request.urlopen(url, context=ctx)
        if resp.getcode() == 200:
            if download:
                data = resp.read()
                path = url.split('/')[-1]
                _mkdir(path)
                open(path.replace(".", '').replace(":", "_"), 'wb').write(data)
            return True
        else:
            return False

    def www_zip_scan(self):
        MODE = "www_zip"
        url = self.url + 'www.zip'
        if self._scan(url, download=True):
            _print("[#] www.zip scaned")
            self.info.append(MODE)
        return

    def git_scan(self):

        MODE = "Git"
        GIT_HOST = self.url + ".git/"
        if self._scan(GIT_HOST):
            self.info.append(MODE)
            import GitHack
            Git = GitHack(GIT_HOST)
            Git.git_init()
            _print("[#] Git scaned")
        return

    def ds_store_scan(self):
        MODE = "DS_Store"
        url = self.url + ".DS_Store/"
        if self._scan(url, download=True):
            self.info.append(MODE)
            _print("[#] DS_Store scaned")
        return

    def vim_swap_scan(self, target_page: str):
        MODE = "VIM_Swap"
        url1 = self.url + "." + target_page + ".swp"
        url2 = self.url + "." + target_page + ".swo"
        l = [url1,url2]
        for i in l:
            if self._scan(i,download=True):
                _print("[#] VIM swap scaned")
        return
    
    
