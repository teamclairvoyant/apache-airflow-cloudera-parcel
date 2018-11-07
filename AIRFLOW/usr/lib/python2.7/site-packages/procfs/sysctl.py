#! /usr/bin/python
# -*- python -*-
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Red Hat, Inc.
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

class sysctl:
	def __init__(self):
		self.cache = {}

	def __getitem__(self, key):
		if not self.cache.has_key(key):
			value = self.read(key)
			if value == None:
				return None
			self.cache[key] = value

		return self.cache[key]

	def __setitem__(self, key, value):
		oldvalue = self[key]

		if oldvalue == None:
			raise IOError
		elif oldvalue != value:
			self.write(key, value)
			self.cache[key] = value

	def keys(self):
		return self.cache.keys()

	def read(self, key):
		try:
			f = file("/proc/sys/%s" % key.replace(".", "/"))
		except:
			return None
		value = f.readline().strip()
		f.close()
		return value

	def write(self, key, value):
		try:
			f = file("/proc/sys/%s" % key.replace(".", "/"), "w")
		except:
			return
		f.write(value)
		f.close()

	def refresh(self):
		for key in self.cache():
			del self.cache[key]
			value = self.read(key)
			if value != None:
				self.cache[key] = value
