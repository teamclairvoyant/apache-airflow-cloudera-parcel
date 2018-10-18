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

def hexbitmask(l, nr_entries):
	hexbitmask = []
	bit = 0
	mask = 0
	for entry in range(nr_entries):
		if entry in l:
			mask |= (1 << bit)
		bit += 1
		if bit == 32:
			bit = 0
			hexbitmask.insert(0, mask)
			mask = 0

	if bit < 32 and mask != 0:
		hexbitmask.insert(0, mask)

	return hexbitmask

def bitmasklist(line, nr_entries):
	hexmask = line.strip().replace(",", "")
	bitmasklist = []
	entry = 0
	bitmask = bin(int(hexmask, 16))[2::]
	for i in reversed(bitmask):
		if int(i) & 1:
			bitmasklist.append(entry)
		entry +=1
		if entry == nr_entries:
			break
	return bitmasklist
