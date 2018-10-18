# -*- coding: utf-8 -*-

#
# Copyright © 2009, 2010, 2012 Red Hat, Inc.
# Authors:
# Nils Philippsen <nils@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module contains helper functions for dealing with files."""

__all__ = ["issamefile", "linkfile", "copyfile", "linkorcopyfile",
           "overwrite_safely"]

import os
import selinux
import shutil
import tempfile
import errno

BLOCKSIZE = 1024


def _issamefile(path1, path2):
    s1 = os.stat(path1)
    s2 = os.stat(path2)

    return os.path.samestat(s1, s2)


def issamefile(path1, path2, catch_stat_exceptions=[]):
    """Check whether two paths point to the same file (i.e. are hardlinked)."""

    if catch_stat_exceptions == True:
        catch_stat_exceptions = Exception

    try:
        return _issamefile(path1, path2)
    except catch_stat_exceptions:
        return False


def linkfile(srcpath, dstpath):
    """Hardlink srcpath to dstpath.

    Attempt to atomically replace dstpath if it exists."""

    if issamefile(srcpath, dstpath, catch_stat_exceptions=OSError):
        return

    dstpath = os.path.abspath(dstpath)
    dstdname = os.path.dirname(dstpath)
    dstbname = os.path.basename(dstpath)

    hardlinked = False
    for attempt in xrange(tempfile.TMP_MAX):
        _dsttmp = tempfile.mktemp(prefix=dstbname + os.extsep, dir=dstdname)
        try:
            os.link(srcpath, _dsttmp)
        except OSError, e:
            if e.errno == errno.EEXIST:

                # try another name

                pass
            else:
                raise
        else:
            hardlinked = True
            break

    if hardlinked:
        os.rename(_dsttmp, dstpath)


def copyfile(srcpath, dstpath, copy_mode_from_dst=True, run_restorecon=True):
    """Copy srcpath to dstpath.

    Abort operation if e.g. not enough space is available.  Attempt to
    atomically replace dstpath if it exists."""

    if issamefile(srcpath, dstpath, catch_stat_exceptions=OSError):
        return

    dstpath = os.path.abspath(dstpath)
    dstdname = os.path.dirname(dstpath)
    dstbname = os.path.basename(dstpath)

    srcfile = open(srcpath, "rb")
    dsttmpfile = tempfile.NamedTemporaryFile(prefix=dstbname + os.path.extsep,
            dir=dstdname, delete=False)

    mode_copied = False

    if copy_mode_from_dst:

        # attempt to copy mode from destination file (if it exists,
        # otherwise fall back to copying it from the source file below)

        try:
            shutil.copymode(dstpath, dsttmpfile.name)
            mode_copied = True
        except (shutil.Error, OSError):
            pass

    if not mode_copied:
        shutil.copymode(srcpath, dsttmpfile.name)

    data = None

    while data != "":
        data = srcfile.read(BLOCKSIZE)
        try:
            dsttmpfile.write(data)
        except:
            srcfile.close()
            dsttmpfile.close()
            os.unlink(dsttmpfile.name)
            raise

    srcfile.close()
    dsttmpfile.close()

    os.rename(dsttmpfile.name, dstpath)

    if run_restorecon and selinux.is_selinux_enabled() > 0:
        selinux.restorecon(dstpath)


def linkorcopyfile(srcpath, dstpath, copy_mode_from_dst=True,
    run_restorecon=True):
    """First attempt to hardlink srcpath to dstpath, if hardlinking isn't
    possible, attempt copying srcpath to dstpath."""

    try:
        linkfile(srcpath, dstpath)
        return
    except OSError, e:
        if e.errno not in (errno.EMLINK, errno.EPERM, errno.EXDEV):

            # don't bother copying

            raise
        else:

            # try copying

            pass

    copyfile(srcpath, dstpath, copy_mode_from_dst, run_restorecon)

def symlink_atomically(srcpath, dstpath, force=False, preserve_context=True):
    """Create a symlink, optionally replacing dstpath atomically, optionally
    setting or preserving SELinux context."""

    dstdname = os.path.dirname(dstpath)
    dstbname = os.path.basename(dstpath)

    run_restorecon = False
    ctx = None

    if preserve_context and selinux.is_selinux_enabled() <= 0:
        preserve_context = False
    else:
        try:
            ret, ctx = selinux.lgetfilecon(dstpath)
            if ret < 0:
                raise RuntimeError("getfilecon(%r) failed" % dstpath)
        except OSError, e:
            if e.errno == errno.ENOENT:
                run_restorecon = True
            else:
                raise

    if not force:
        os.symlink(srcpath, dstpath)
        if preserve_context:
            selinux.restorecon(dstpath)
    else:
        dsttmp = None
        for attempt in xrange(tempfile.TMP_MAX):
            _dsttmp = tempfile.mktemp(prefix=dstbname + os.extsep, dir=dstdname)
            try:
                os.symlink(srcpath, _dsttmp)
            except OSError, e:
                if e.errno == errno.EEXIST:
                    # try again
                    continue
                raise
            else:
                dsttmp = _dsttmp
                break

        if dsttmp is None:
            raise IOError(errno.EEXIST,
                    "No suitable temporary symlink could be created.")

        if preserve_context and not run_restorecon:
            selinux.lsetfilecon(dsttmp, ctx)

        try:
            os.rename(dsttmp, dstpath)
        except:
            # clean up
            os.remove(dsttmp)
            raise

        if run_restorecon:
            selinux.restorecon(dstpath)

def overwrite_safely(path, content, preserve_mode=True, preserve_context=True):
    """Safely overwrite a file by creating a temporary file in the same
    directory, writing it, moving it over the original file, eventually
    preserving file mode and SELinux context."""

    path = os.path.realpath(path)
    dir_ = os.path.dirname(path)
    base = os.path.basename(path)

    fd = None
    f = None
    tmpname = None

    exists = os.path.exists(path)

    if preserve_context and selinux.is_selinux_enabled() <= 0:
        preserve_context = False

    try:
        fd, tmpname = tempfile.mkstemp(prefix=base + os.path.extsep,
                                       dir=dir_)

        if exists and preserve_mode:
            shutil.copymode(path, tmpname)

        if exists and preserve_context:
            ret, ctx = selinux.getfilecon(path)
            if ret < 0:
                raise RuntimeError("getfilecon(%r) failed" % path)

        f = os.fdopen(fd, "w")
        fd = None

        f.write(content)

        f.close()
        f = None

        os.rename(tmpname, path)

        if preserve_context:
            if exists:
                selinux.setfilecon(path, ctx)
            else:
                selinux.restorecon(path)

    finally:
        if f:
            f.close()
        elif fd:
            os.close(fd)
        if tmpname and os.path.isfile(tmpname):
            try:
                os.unlink(tmpname)
            except:
                pass
