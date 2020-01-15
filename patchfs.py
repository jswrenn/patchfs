#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations

class Passthrough(Operations):
    def __init__(self, root, patch):
        self.root = root
        self.patch = patch

    # Helpers
    # =======

    def _root_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    def _patch_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.patch, partial)
        return path

    def _choose(self, path):
        root_path = self._root_path(path)
        patch_path = self._patch_path(path)
        if os.path.exists(patch_path):
            return patch_path
        else:
            return root_path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._choose(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        raise FuseOSError(EROFS)

    def chown(self, path, uid, gid):
        raise FuseOSError(EROFS)

    def getattr(self, path, fh=None):
        full_path = self._choose(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        root_path = self._root_path(path)
        patch_path = self._patch_path(path)

        dirents = ['.', '..']

        if os.path.isdir(root_path):
            dirents.extend(os.listdir(root_path))

        if os.path.isdir(patch_path):
            dirents.extend(os.listdir(patch_path))

        deduped = list(dict.fromkeys(dirents))

        for r in deduped:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._choose(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        raise FuseOSError(EROFS)

    def rmdir(self, path):
        raise FuseOSError(EROFS)

    def mkdir(self, path, mode):
        raise FuseOSError(EROFS)

    def statfs(self, path):
        full_path = self._choose(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        raise FuseOSError(EROFS)

    def symlink(self, name, target):
        raise FuseOSError(EROFS)

    def rename(self, old, new):
        raise FuseOSError(EROFS)

    def link(self, target, name):
        raise FuseOSError(EROFS)

    def utimens(self, path, times=None):
        raise FuseOSError(EROFS)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._choose(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        raise FuseOSError(EROFS)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        raise FuseOSError(EROFS)

    def truncate(self, path, length, fh=None):
        raise FuseOSError(EROFS)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root, patch):
    FUSE(Passthrough(root, patch), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[3], sys.argv[1], sys.argv[2])
