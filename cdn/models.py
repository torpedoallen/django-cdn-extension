# coding=utf8

import re
import os
import json
import hashlib
import urlparse
from django.conf import settings


def load_hash():
    with open('static/__hash__.json') as data_file:
        pool = json.load(data_file)
    return pool


def save_hash(pool):
    with open('static/__hash__.json', 'wb') as data_file:
        json.dump(pool, data_file, sort_keys=True, indent=4)


def wrap_url(url, hash_, limit=8):
    """
    >>> wrap_url('/image/a.png', '123')
    '/image/a.123.png'
    >>> wrap_url('http://static.example.com/image/a.png', '123')
    'http://static.example.com/image/a.123.png'
    >>> wrap_url('http://static.example.com/image/a', '123')
    'http://static.example.com/image/a.123'
    """
    hash_ = hash_[:limit]
    p = urlparse.urlparse(url)
    path_split = p.path.split('/')
    name_split = path_split[-1].split('.')
    if len(name_split) > 1:
        name_split.insert(-1, hash_)
    else:
        name_split.append(hash_)
    name = '.'.join(name_split)
    path_split[-1] = name
    new_path = '/'.join(path_split)
    new_result = urlparse.ParseResult(
        scheme=p.scheme,
        netloc=p.netloc,
        path=new_path,
        params=p.params,
        query=p.query,
        fragment=p.fragment)
    return urlparse.urlunparse(new_result)


class StaticFile(object):


    (STATIC_NEW, STATIC_UPDATE, STATIC_EQUAL) = range(3)

    def __init__(self, path, prefix=settings.ONLINE_STATIC_ROOT):
        if path.startswith('/'):
            path = path[1:]
        self.path = path
        self.prefix = prefix

    @property
    def __hashes__(self):
        return load_hash()

    @classmethod
    def get_all_statics(cls):
        _patterns = [r.strip() for r in open('.gitignore') if r]
        for x in os.walk(settings.STATIC_ROOT):
            for name in x[2]:
                is_ignored = False
                path = '%s/%s' % (x[0], name)
                for p in _patterns:
                    if re.search(p.replace('*', ''), path):
                        is_ignored = True
                        break
                if is_ignored:
                    continue
                yield path

    @property
    def md5(self):
        return hashlib.md5(open(self.path, 'rb').read()).hexdigest()

    @property
    def rel_path(self):
        return self.path[len(self.prefix)+1:]

    @property
    def cdn_path(self):
        return '%s/%s' % (settings.CDN_FINDER_PREFIX, self.cdn_name)

    def register(self, pool):
        if self.rel_path not in pool:
            pool[self.rel_path] = self.md5
            return self.STATIC_NEW

        new_md5 = self.md5
        if pool[self.rel_path] != new_md5:
            pool[self.rel_path] = new_md5
            return self.STATIC_UPDATE
        return self.STATIC_EQUAL

    @property
    def cdn_name(self):
        hash_ = self.__hashes__.get(self.rel_path)
        return wrap_url(self.rel_path, hash_)

    def upload(self):
        # your uploading logic
        pass

def serve():
    pool = load_hash()
    deltas = []
    for x in StaticFile.get_all_statics():
        f = StaticFile(x, prefix=settings.STATIC_ROOT)
        ret = f.register(pool)
        if ret != StaticFile.STATIC_EQUAL:
            deltas.append(f)
    save_hash(pool)
    for f in deltas:
        f.upload()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    #serve()
