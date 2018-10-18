#! /usr/bin/python
# -*- python -*-
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008, 2009 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
"""
Copyright (c) 2008, 2009  Red Hat Inc.

Abstractions to extract information from the Linux kernel /proc files.
"""
__author__ = "Arnaldo Carvalho de Melo <acme@redhat.com>"
__license__ = "GPLv2 License"

from procfs import *
from sysctl import *
from utilist import *
