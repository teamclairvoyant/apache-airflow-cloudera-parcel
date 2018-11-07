## Copyright (C) 2013 ABRT team <abrt-devel-list@redhat.com>
## Copyright (C) 2013 Red Hat, Inc.

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Suite 500, Boston, MA  02110-1335  USA

import logging

VERBOSITY = 0


def set_verbosity(verbosity):
    global VERBOSITY
    VERBOSITY = verbosity


def getLogger():
    logger = logging.getLogger('abrt-screencast')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    #ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

    return logger

LOGGER = getLogger()


def __args_to_str(*args):
    return ",".join(map(str, args))


def info(*args):
    if VERBOSITY > 1:
        LOGGER.info(__args_to_str(*args))


def warn(*args):
    if VERBOSITY > 0:
        LOGGER.warn(__args_to_str(*args))


def error(*args):
    LOGGER.error(__args_to_str(*args))
