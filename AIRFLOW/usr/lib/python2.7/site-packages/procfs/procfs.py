#! /usr/bin/python
# -*- python -*-
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2015 Red Hat, Inc.
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

import os, time, utilist

VERSION="0.3"

def process_cmdline(pid_info):
	"""
	Returns the process command line, if available in the given `process' class, if
	not available, falls back to using the comm (short process name) in its pidstat key.
	"""
	if pid_info["cmdline"]:
		return reduce(lambda a, b: a + " %s" % b, pid_info["cmdline"]).strip()

	return pid_info["stat"]["comm"]

class pidstat:
	"""Provides a dictionary to access the fields in the per process /proc/PID/stat
	   files.

	   One can obtain the available fields asking for the keys of the dictionary, e.g.:

		>>> p = procfs.pidstat(1)
		>>> print p.keys()
		['majflt', 'rss', 'cnswap', 'cstime', 'pid', 'session', 'startstack', 'startcode', 'cmajflt', 'blocked', 'exit_signal', 'minflt', 'nswap', 'environ', 'priority', 'state', 'delayacct_blkio_ticks', 'policy', 'rt_priority', 'ppid', 'nice', 'cutime', 'endcode', 'wchan', 'num_threads', 'sigcatch', 'comm', 'stime', 'sigignore', 'tty_nr', 'kstkeip', 'utime', 'tpgid', 'itrealvalue', 'kstkesp', 'rlim', 'signal', 'pgrp', 'flags', 'starttime', 'cminflt', 'vsize', 'processor']

	   And then access the various process properties using it as a dictionary:

		>>> print p['comm']
		systemd
		>>> print p['priority']
		20
		>>> print p['state']
		S

	   Please refer to the 'procfs(5)' man page, by using:

		$ man 5 procfs

	   To see information for each of the above fields, it is part of the
           'man-pages' RPM package.
	"""

	# Entries with the same value, the one with a comment after it is the
	# more recent, having replaced the other name in v4.1-rc kernel times.

	PF_ALIGNWARN	 = 0x00000001
	PF_STARTING	 = 0x00000002
	PF_EXITING	 = 0x00000004
	PF_EXITPIDONE	 = 0x00000008
	PF_VCPU		 = 0x00000010
	PF_WQ_WORKER	 = 0x00000020 # /* I'm a workqueue worker */
	PF_FORKNOEXEC	 = 0x00000040
	PF_MCE_PROCESS	 = 0x00000080 # /* process policy on mce errors */
	PF_SUPERPRIV	 = 0x00000100
	PF_DUMPCORE	 = 0x00000200
	PF_SIGNALED	 = 0x00000400
	PF_MEMALLOC	 = 0x00000800
	PF_NPROC_EXCEEDED= 0x00001000 # /* set_user noticed that RLIMIT_NPROC was exceeded */
	PF_FLUSHER	 = 0x00001000
	PF_USED_MATH	 = 0x00002000
	PF_USED_ASYNC	 = 0x00004000 # /* used async_schedule*(), used by module init */
	PF_NOFREEZE	 = 0x00008000
	PF_FROZEN	 = 0x00010000
	PF_FSTRANS	 = 0x00020000
	PF_KSWAPD	 = 0x00040000
	PF_MEMALLOC_NOIO = 0x00080000 # /* Allocating memory without IO involved */
	PF_SWAPOFF	 = 0x00080000
	PF_LESS_THROTTLE = 0x00100000
	PF_KTHREAD	 = 0x00200000
	PF_RANDOMIZE	 = 0x00400000
	PF_SWAPWRITE	 = 0x00800000
	PF_SPREAD_PAGE	 = 0x01000000
	PF_SPREAD_SLAB	 = 0x02000000
	PF_THREAD_BOUND	 = 0x04000000
	PF_NO_SETAFFINITY = 0x04000000 # /* Userland is not allowed to meddle with cpus_allowed */
	PF_MCE_EARLY	 = 0x08000000 # /* Early kill for mce process policy */
	PF_MEMPOLICY	 = 0x10000000
	PF_MUTEX_TESTER	 = 0x20000000
	PF_FREEZER_SKIP	 = 0x40000000
	PF_FREEZER_NOSIG = 0x80000000
	PF_SUSPEND_TASK	 = 0x80000000 # /* this thread called freeze_processes and should not be frozen */

	proc_stat_fields = [ "pid", "comm", "state", "ppid", "pgrp", "session",
			     "tty_nr", "tpgid", "flags", "minflt", "cminflt",
			     "majflt", "cmajflt", "utime", "stime", "cutime",
			     "cstime", "priority", "nice", "num_threads",
			     "itrealvalue", "starttime", "vsize", "rss",
			     "rlim", "startcode", "endcode", "startstack",
			     "kstkesp", "kstkeip", "signal", "blocked",
			     "sigignore", "sigcatch", "wchan", "nswap",
			     "cnswap", "exit_signal", "processor",
			     "rt_priority", "policy",
			     "delayacct_blkio_ticks", "environ" ]

	def __init__(self, pid, basedir = "/proc"):
		self.pid = pid
		self.load(basedir)

	def __getitem__(self, fieldname):
		return self.fields[fieldname]

	def keys(self):
		return self.fields.keys()

	def values(self):
		return self.fields.values()

	def has_key(self, fieldname):
		return self.fields.has_key(fieldname)

	def items(self):
		return self.fields

	def __contains__(self, fieldname):
		return fieldname in self.fields

	def load(self, basedir = "/proc"):
		f = open("%s/%d/stat" % (basedir, self.pid))
		fields = f.readline().strip().split(') ')
		f.close()
		fields = fields[0].split(' (') + fields[1].split()
		self.fields = {}
		nr_fields = min(len(fields), len(self.proc_stat_fields))
		for i in range(nr_fields):
			attrname = self.proc_stat_fields[i]
			value = fields[i]
			if attrname == "comm":
				self.fields["comm"] = value.strip('()')
			else:
				try:
					self.fields[attrname] = int(value)
				except:
					self.fields[attrname] = value

	def is_bound_to_cpu(self):
		"""
		Returns true if this process has a fixed smp affinity mask,
                not allowing it to be moved to a different set of CPUs.
		"""
		return self.fields["flags"] & self.PF_THREAD_BOUND and \
			True or False

	def process_flags(self):
		"""
		Returns a list with all the process flags known, details depend
		on kernel version, declared in the file include/linux/sched.h in
		the kernel sources.

		As of v4.2-rc7 these include (from include/linux/sched.h comments):

			PF_EXITING	   Getting shut down
			PF_EXITPIDONE	   Pi exit done on shut down
			PF_VCPU		   I'm a virtual CPU
			PF_WQ_WORKER	   I'm a workqueue worker
			PF_FORKNOEXEC	   Forked but didn't exec
			PF_MCE_PROCESS	   Process policy on mce errors
			PF_SUPERPRIV	   Used super-user privileges
			PF_DUMPCORE	   Dumped core
			PF_SIGNALED	   Killed by a signal
			PF_MEMALLOC	   Allocating memory
			PF_NPROC_EXCEEDED  Set_user noticed that RLIMIT_NPROC was exceeded
			PF_USED_MATH	   If unset the fpu must be initialized before use
			PF_USED_ASYNC	   Used async_schedule*(), used by module init
			PF_NOFREEZE	   This thread should not be frozen
			PF_FROZEN	   Frozen for system suspend
			PF_FSTRANS	   Inside a filesystem transaction
			PF_KSWAPD	   I am kswapd
			PF_MEMALLOC_NOIO   Allocating memory without IO involved
			PF_LESS_THROTTLE   Throttle me less: I clean memory
			PF_KTHREAD	   I am a kernel thread
			PF_RANDOMIZE	   Randomize virtual address space
			PF_SWAPWRITE	   Allowed to write to swap
			PF_NO_SETAFFINITY  Userland is not allowed to meddle with cpus_allowed
			PF_MCE_EARLY	   Early kill for mce process policy
			PF_MUTEX_TESTER	   Thread belongs to the rt mutex tester
			PF_FREEZER_SKIP	   Freezer should not count it as freezable
			PF_SUSPEND_TASK	   This thread called freeze_processes and should not be frozen
	
		"""
		sflags = []
		for attr in dir(self):
			if attr[:3] != "PF_":
				continue
			value = getattr(self, attr)
			if value & self.fields["flags"]:
				sflags.append(attr)

		return sflags

class pidstatus:
	"""
	Provides a dictionary to access the fields in the per process /proc/PID/status
	files. This provides additional information about processes and threads to what
	can be obtained with the procfs.pidstat() class.

	One can obtain the available fields asking for the keys of the dictionary, e.g.:

		>>> import procfs
		>>> p = procfs.pidstatus(1)
		>>> print p.keys()
		['VmExe', 'CapBnd', 'NSpgid', 'Tgid', 'NSpid', 'VmSize', 'VmPMD', 'ShdPnd', 'State', 'Gid', 'nonvoluntary_ctxt_switches', 'SigIgn', 'VmStk', 'VmData', 'SigCgt', 'CapEff', 'VmPTE', 'Groups', 'NStgid', 'Threads', 'PPid', 'VmHWM', 'NSsid', 'VmSwap', 'Name', 'SigBlk', 'Mems_allowed_list', 'VmPeak', 'Ngid', 'VmLck', 'SigQ', 'VmPin', 'Mems_allowed', 'CapPrm', 'Seccomp', 'VmLib', 'Cpus_allowed', 'Uid', 'SigPnd', 'Pid', 'Cpus_allowed_list', 'TracerPid', 'CapInh', 'voluntary_ctxt_switches', 'VmRSS', 'FDSize']
		>>> print p["Pid"]
		1
		>>> print p["Threads"]
		1
		>>> print p["VmExe"]
		1248 kB
		>>> print p["Cpus_allowed"]
		f
		>>> print p["SigQ"]
		0/30698
		>>> print p["VmPeak"]
		320300 kB
		>>>

	Please refer to the 'procfs(5)' man page, by using:

		$ man 5 procfs

	To see information for each of the above fields, it is part of the
	'man-pages' RPM package.

	In the man page there will be references to further documentation, like
        referring to the "getrlimit(2)" man page when explaining the "SigQ"
        line/field.
	"""

	def __init__(self, pid, basedir = "/proc"):
		self.pid = pid
		self.load(basedir)

	def __getitem__(self, fieldname):
		return self.fields[fieldname]

	def keys(self):
		return self.fields.keys()

	def values(self):
		return self.fields.values()

	def has_key(self, fieldname):
		return self.fields.has_key(fieldname)

	def items(self):
		return self.fields

	def __contains__(self, fieldname):
		return fieldname in self.fields

	def load(self, basedir = "/proc"):
		f = open("%s/%d/status" % (basedir, self.pid))
		self.fields = {}
		for line in f.readlines():
			fields = line.split(":")
			if len(fields) != 2:
				continue
			name = fields[0]
			value = fields[1].strip()
			try:
				self.fields[name] = int(value)
			except:
				self.fields[name] = value
		f.close()

class process:
	"""
	Information about a process with a given pid, provides a dictionary with
	two entries, instances of different wrappers for /proc/ process related
	meta files: "stat" and "status", see the documentation for procfs.pidstat
	and procfs.pidstatus for further info about those classes.
	"""

	def __init__(self, pid, basedir = "/proc"):
		self.pid = pid
		self.basedir = basedir

	def __getitem__(self, attr):
		if not hasattr(self, attr):
			if attr in ("stat", "status"):
				if attr == "stat":
					sclass = pidstat
				else:
					sclass = pidstatus

				setattr(self, attr, sclass(self.pid, self.basedir))
			elif attr == "cmdline":
				self.load_cmdline()
			elif attr == "threads":
				self.load_threads()
			elif attr == "cgroups":
				self.load_cgroups()
			elif attr == "environ":
				self.load_environ()

		return getattr(self, attr)

	def has_key(self, attr):
		return hasattr(self, attr)

	def __contains__(self, attr):
		return hasattr(self, attr)

	def load_cmdline(self):
		f = file("/proc/%d/cmdline" % self.pid)
		self.cmdline = f.readline().strip().split('\0')[:-1]
		f.close()

	def load_threads(self):
		self.threads = pidstats("/proc/%d/task/" % self.pid)
		# remove thread leader
		del self.threads[self.pid]

	def load_cgroups(self):
		f = file("/proc/%d/cgroup" % self.pid)
		self.cgroups = ""
		for line in reversed(f.readlines()):
			if len(self.cgroups):
				self.cgroups = self.cgroups + "," + line[:-1]
			else:
				self.cgroups = line[:-1]
		f.close()

	def load_environ(self):
		"""
		Loads the environment variables for this process. The entries then
		become available via the 'environ' member, or via the 'environ'
		dict key when accessing as p["environ"].

		E.g.:


		>>> all_processes = procfs.pidstats()
		>>> firefox_pid = all_processes.find_by_name("firefox")
		>>> firefox_process = all_processes[firefox_pid[0]]
		>>> print firefox_process["environ"]["PWD"]
		/home/acme
		>>> print len(firefox_process.environ.keys())
		66
		>>> print firefox_process["environ"]["SHELL"]
		/bin/bash
		>>> print firefox_process["environ"]["USERNAME"]
		acme
		>>> print firefox_process["environ"]["HOME"]
		/home/acme
		>>> print firefox_process["environ"]["MAIL"]
		/var/spool/mail/acme
		>>>
		"""
		self.environ = {}
		f = file("/proc/%d/environ" % self.pid)
		for x in f.readline().split('\0'):
			if len(x) > 0:
				y = x.split('=')
				self.environ[y[0]] = y[1]
		f.close()

class pidstats:
	"""
	Provides access to all the processes in the system, to get a picture of
	how many processes there are at any given moment.

	The entries can be accessed as a dictionary, keyed by pid. Also there are
	methods to find processes that match a given COMM or regular expression.
	"""
	def __init__(self, basedir = "/proc"):
		self.basedir = basedir
		self.processes = {}
		self.reload()

	def __getitem__(self, key):
		return self.processes[key]

	def __delitem__(self, key):
		# not clear on why this can fail, but it can
		try:
			del self.processes[key]
		except:
			pass

	def keys(self):
		return self.processes.keys()

	def values(self):
		return self.processes.values()

	def has_key(self, key):
		return self.processes.has_key(key)

	def items(self):
		return self.processes

	def __contains__(self, key):
		return key in self.processes

	def reload(self):
		"""
		This operation will throw away the current dictionary contents, if any, and
		read all the pid files from /proc/, instantiating a 'process' instance for
		each of them.

		This is a high overhead operation, and should be avoided if the perf python
		binding can be used to detect when new threads appear and existing ones
		terminate.

		In RHEL it is found in the python-perf rpm package.

		More information about the perf facilities can be found in the 'perf_event_open'
		man page.
		"""
		del self.processes
		self.processes = {}
		pids = os.listdir(self.basedir)
		for spid in pids:
			try:
				pid = int(spid)
			except:
				continue

			self.processes[pid] = process(pid, self.basedir)

	def reload_threads(self):
		for pid in self.processes.keys():
			try:
				self.processes[pid].load_threads()
			except OSError:
				# process vanished, remove it
				del self.processes[pid]

	def find_by_name(self, name):
		name = name[:15]
		pids = []
		for pid in self.processes.keys():
			try:
				if name == self.processes[pid]["stat"]["comm"]:
					pids.append(pid)
			except IOError:
				# We're doing lazy loading of /proc files
				# So if we get this exception is because the
				# process vanished, remove it
				del self.processes[pid]
				
		return pids

	def find_by_regex(self, regex):
		pids = []
		for pid in self.processes.keys():
			try:
				if regex.match(self.processes[pid]["stat"]["comm"]):
					pids.append(pid)
			except IOError:
				# We're doing lazy loading of /proc files
				# So if we get this exception is because the
				# process vanished, remove it
				del self.processes[pid]
		return pids

	def find_by_cmdline_regex(self, regex):
		pids = []
		for pid in self.processes.keys():
			try:
				if regex.match(process_cmdline(self.processes[pid])):
					pids.append(pid)
			except IOError:
				# We're doing lazy loading of /proc files
				# So if we get this exception is because the
				# process vanished, remove it
				del self.processes[pid]
		return pids

	def get_per_cpu_rtprios(self, basename):
		cpu = 0
		priorities=""
		processed_pids = []
		while True:
			name = "%s/%d" % (basename, cpu)
			pids = self.find_by_name(name)
			if not pids or len([n for n in pids if n not in processed_pids]) == 0:
				break
			for pid in pids:
				try:
					priorities += "%s," % self.processes[pid]["stat"]["rt_priority"]
				except IOError:
					# We're doing lazy loading of /proc files
					# So if we get this exception is because the
					# process vanished, remove it
					del self.processes[pid]
			processed_pids += pids
			cpu += 1

		priorities = priorities.strip(',')
		return priorities

	def get_rtprios(self, name):
		cpu = 0
		priorities=""
		processed_pids = []
		while True:
			pids = self.find_by_name(name)
			if not pids or len([n for n in pids if n not in processed_pids]) == 0:
				break
			for pid in pids:
				try:
					priorities += "%s," % self.processes[pid]["stat"]["rt_priority"]
				except IOError:
					# We're doing lazy loading of /proc files
					# So if we get this exception is because the
					# process vanished, remove it
					del self.processes[pid]
			processed_pids += pids
			cpu += 1

		priorities = priorities.strip(',')
		return priorities

	def is_bound_to_cpu(self, pid):
		"""
		Checks if a given pid can't have its SMP affinity mask changed.
		"""
		return self.processes[pid]["stat"].is_bound_to_cpu()

class interrupts:
	"""
	Information about IRQs in the system. A dictionary keyed by IRQ number
	will have as its value another dictionary with "cpu", "type" and "users"
	keys, with the SMP affinity mask, type of IRQ and the drivers associated
	with each interrupt.

	The information comes from the /proc/interrupts file, documented in
	'man procfs(5)', for instance, the 'cpu' dict is an array with one entry
	per CPU present in the sistem, each value being the number of interrupts
	that took place per CPU.

	E.g.:

	>>> import procfs
	>>> interrupts = procfs.interrupts()
	>>> thunderbolt_irq = interrupts.find_by_user("thunderbolt")
	>>> print thunderbolt_irq
	34
	>>> thunderbolt = interrupts[thunderbolt_irq]
	>>> print thunderbolt
	{'affinity': [0, 1, 2, 3], 'type': 'PCI-MSI', 'cpu': [3495, 0, 81, 0], 'users': ['thunderbolt']}
	>>>
	"""
	def __init__(self):
		self.interrupts = {}
		self.reload()

	def __getitem__(self, key):
		return self.interrupts[str(key)]

	def keys(self):
		return self.interrupts.keys()

	def values(self):
		return self.interrupts.values()

	def has_key(self, key):
		return self.interrupts.has_key(str(key))

	def items(self):
		return self.interrupts

	def __contains__(self, key):
		return str(key) in self.interrupts

	def reload(self):
		del self.interrupts
		self.interrupts = {}
		f = open("/proc/interrupts")

		for line in f.readlines():
			line = line.strip()
			fields = line.split()
			if fields[0][:3] == "CPU":
				self.nr_cpus = len(fields)
				continue
			irq = fields[0].strip(":")
			self.interrupts[irq] = {}
			self.interrupts[irq] = self.parse_entry(fields[1:], line)
			try:
				nirq = int(irq)
			except:
				continue
			self.interrupts[irq]["affinity"] = self.parse_affinity(nirq)

		f.close()

	def parse_entry(self, fields, line):
		dict = {}
		dict["cpu"] = []
		dict["cpu"].append(int(fields[0]))
		nr_fields = len(fields)
		if nr_fields >= self.nr_cpus:
			dict["cpu"] += [int(i) for i in fields[1:self.nr_cpus]]
			if nr_fields > self.nr_cpus:
				dict["type"] = fields[self.nr_cpus]
				# look if there are users (interrupts 3 and 4 haven't)
				if nr_fields > self.nr_cpus + 1:
					dict["users"] = [a.strip() for a in fields[nr_fields - 1].split(',')]
				else:
					dict["users"] = []
		return dict

	def parse_affinity(self, irq):
		try:
			f = file("/proc/irq/%s/smp_affinity" % irq)
			line = f.readline()
			f.close()
			return utilist.bitmasklist(line, self.nr_cpus)
		except IOError:
			return [ 0, ]

	def find_by_user(self, user):
		"""
		Looks up a interrupt number by the name of one of its users"

		E.g.:

		>>> import procfs
		>>> interrupts = procfs.interrupts()
		>>> thunderbolt_irq = interrupts.find_by_user("thunderbolt")
		>>> print thunderbolt_irq
		34
		>>> thunderbolt = interrupts[thunderbolt_irq]
		>>> print thunderbolt
		{'affinity': [0, 1, 2, 3], 'type': 'PCI-MSI', 'cpu': [3495, 0, 81, 0], 'users': ['thunderbolt']}
		>>>
		"""
		for i in self.interrupts.keys():
			if self.interrupts[i].has_key("users") and \
			   user in self.interrupts[i]["users"]:
				return i
		return None

	def find_by_user_regex(self, regex):
		"""
		Looks up a interrupt number by a regex that matches names of its users"

		E.g.:

		>>> import procfs
		>>> import re
		>>> interrupts = procfs.interrupts()
		>>> usb_controllers = interrupts.find_by_user_regex(re.compile(".*hcd"))
		>>> print usb_controllers
		['22', '23', '31']
		>>> print [ interrupts[irq]["users"] for irq in usb_controllers ]
		[['ehci_hcd:usb4'], ['ehci_hcd:usb3'], ['xhci_hcd']]
		>>>
		"""
		irqs = []
		for i in self.interrupts.keys():
			if not self.interrupts[i].has_key("users"):
				continue
			for user in self.interrupts[i]["users"]:
				if regex.match(user):
					irqs.append(i)
					break
		return irqs

class cmdline:
	"""
	Parses the kernel command line (/proc/cmdline), turning it into a dictionary."

	Useful to figure out if some kernel boolean knob has been turned on, as well
	as to find the value associated to other kernel knobs.

	It can also be used to find out about parameters passed to the init process,
	such as 'BOOT_IMAGE', etc.

	E.g.:
	>>> import procfs
	>>> kcmd = procfs.cmdline()
	>>> print kcmd.keys()
	['LANG', 'BOOT_IMAGE', 'quiet', 'rhgb', 'rd.lvm.lv', 'ro', 'root']
	>>> print kcmd["BOOT_IMAGE"]
	/vmlinuz-4.3.0-rc1+
	>>>
	"""

	def __init__(self):
		self.options = {}
		self.parse()

	def parse(self):
		f = file("/proc/cmdline")
		for option in f.readline().strip().split():
			fields = option.split("=")
			if len(fields) == 1:
				self.options[fields[0]] = True
			else:
				self.options[fields[0]] = fields[1]

		f.close()

	def __getitem__(self, key):
		return self.options[key]

	def keys(self):
		return self.options.keys()

	def values(self):
		return self.options.values()

	def items(self):
		return self.options

class cpuinfo:
	"""
	Dictionary with information about CPUs in the system.

	Please refer to 'man procfs(5)' for further information about the
        '/proc/cpuinfo' file, that is the source of the information provided by this
        class. The 'man lscpu(1)' also has information about a program that uses
	the '/proc/cpuinfo' file.

	Using this class one can obtain the number of CPUs in a system:

	  >>> cpus = procfs.cpuinfo()
          >>> print cpus.nr_cpus
          4

	It is also possible to figure out aspects of the CPU topology, such as
	how many CPU physical sockets exists, i.e. groups of CPUs sharing components
	such as CPU memory caches:

	  >>> print len(cpus.sockets)
	  1

	Additionally dictionary with information common to all CPUs in the system is
	available:

	  >>> print cpus["model name"]
          Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz
          >>> print cpus["cache size"]
          4096 KB
          >>>
	"""
	def __init__(self, filename="/proc/cpuinfo"):
		self.tags = {}
		self.nr_cpus = 0
		self.sockets = []
		self.parse(filename)

	def __getitem__(self, key):
		return self.tags[key.lower()]

	def keys(self):
		return self.tags.keys()

	def values(self):
		return self.tags.values()

	def items(self):
		return self.tags

	def parse(self, filename):
		f = file(filename)
		for line in f.readlines():
			line = line.strip()
			if len(line) == 0:
				continue
			fields = line.split(":")
			tagname = fields[0].strip().lower()
			if tagname == "processor":
				self.nr_cpus += 1
				continue
			elif tagname == "core id":
				continue
			self.tags[tagname] = fields[1].strip()
			if tagname == "physical id":
				socket_id = self.tags[tagname]
				if socket_id not in self.sockets:
					self.sockets.append(socket_id)

		f.close()
		self.nr_sockets = self.sockets and len(self.sockets) or \
				  (self.nr_cpus / ("siblings" in self.tags and int(self.tags["siblings"]) or 1))
		self.nr_cores = ("cpu cores" in self.tags and int(self.tags["cpu cores"]) or 1) * self.nr_sockets

class smaps_lib:
	"""
	Representation of an mmap in place for a process. Can be used to figure
	out which processes have an library mapped, etc.

	The 'perm' member can be used to figure out executable mmaps, i.e. libraries.

	The 'vm_start' and 'vm_end' in turn can be used when trying to resolve
	processor instruction pointer addresses to a symbol name in a library.
	"""
	def __init__(self, lines):
		fields = lines[0].split()
		self.vm_start, self.vm_end = map(lambda a: int(a, 16), fields[0].split("-"))
		self.perms = fields[1]
		self.offset = int(fields[2], 16)
		self.major, self.minor = fields[3].split(":")
		self.inode = int(fields[4])
		if len(fields) > 5:
			self.name = fields[5]
		else:
			self.name = None
		self.tags = {}
		for line in lines[1:]:
			fields = line.split()
			tag = fields[0][:-1].lower()
			try:
				self.tags[tag] = int(fields[1])
			except:
				# VmFlags are strings
				self.tags[tag] = fields

	def __getitem__(self, key):
		return self.tags[key.lower()]

	def keys(self):
		return self.tags.keys()

	def values(self):
		return self.tags.values()

	def items(self):
		return self.tags


class smaps:
	"""
	List of libraries mapped by a process. Parses the lines in
	the /proc/PID/smaps file, that is further documented in the
	procfs(5) man page.

	Example: Listing the executable maps for the 'sshd' process:

          >>> import procfs
          >>> processes = procfs.pidstats()
          >>> sshd = processes.find_by_name("sshd")
          >>> sshd_maps = procfs.smaps(sshd[0])
          >>> for i in range(len(sshd_maps)):
          ...     if 'x' in sshd_maps[i].perms:
          ...         print "%s: %s" % (sshd_maps[i].name, sshd_maps[i].perms)
          ...
          /usr/sbin/sshd: r-xp
          /usr/lib64/libnss_files-2.20.so: r-xp
          /usr/lib64/librt-2.20.so: r-xp
          /usr/lib64/libkeyutils.so.1.5: r-xp
          /usr/lib64/libkrb5support.so.0.1: r-xp
          /usr/lib64/libfreebl3.so: r-xp
          /usr/lib64/libpthread-2.20.so: r-xp
	  ...
	"""
	def __init__(self, pid):
		self.pid = pid
		self.entries = []
		self.reload()

	def parse_entry(self, f, line):
		lines = []
		if not line:
			line = f.readline().strip()
		if not line:
			return
		lines.append(line)
		while True:
			line = f.readline()
			if not line:
				break
			line = line.strip()
			if line.split()[0][-1] == ':':
				lines.append(line)
			else:
				break
		self.entries.append(smaps_lib(lines))
		return line

	def __len__(self):
		return len(self.entries)

	def __getitem__(self, index):
		return self.entries[index]

	def reload(self):
		f = file("/proc/%d/smaps" % self.pid)
		line = None
		while True:
			line = self.parse_entry(f, line)
			if not line:
				break
		f.close()
		self.nr_entries = len(self.entries)

	def find_by_name_fragment(self, fragment):
		result = []
		for i in range(self.nr_entries):
			if self.entries[i].name and \
			   self.entries[i].name.find(fragment) >= 0:
			   	result.append(self.entries[i])
				
		return result

class cpustat:
	"""
	CPU statistics, obtained from a line in the '/proc/stat' file, Please
	refer to 'man procfs(5)' for further information about the '/proc/stat'
	file, that is the source of the information provided by this class.
	"""

	def __init__(self, fields):
		self.name = fields[0]
		(self.user,
		 self.nice,
		 self.system,
		 self.idle,
		 self.iowait,
		 self.irq,
		 self.softirq) = [int(i) for i in fields[1:8]]
		if len(fields) > 7:
			self.steal = int(fields[7])
			if len(fields) > 8:
				self.guest = int(fields[8])

	def __repr__(self):
		s = "< user: %s, nice: %s, system: %s, idle: %s, iowait: %s, irq: %s, softirq: %s" % \
			(self.user, self.nice, self.system, self.idle, self.iowait, self.irq, self.softirq)
		if hasattr(self, 'steal'):
			s += ", steal: %d" % self.steal
		if hasattr(self, 'guest'):
			s += ", guest: %d" % self.guest
		return s + ">"

class cpusstats:
	"""
	Dictionary with information about CPUs in the system. First entry in the
	dictionary gives an aggregate view of all CPUs, each other entry is about
	separate CPUs. Please refer to 'man procfs(5)' for further information
	about the '/proc/stat' file, that is the source of the information provided
	by this class.
	"""
	def __init__(self, filename = "/proc/stat"):
		self.entries = {}
		self.time = None
		self.hertz = os.sysconf(2)
		self.filename = filename
		self.reload()

	def __iter__(self):
		return iter(self.entries)

	def __getitem__(self, key):
		return self.entries[key]

	def __len__(self):
		return len(self.entries.keys())

	def keys(self):
		return self.entries.keys()

	def values(self):
		return self.entries.values()

	def items(self):
		return self.entries

	def reload(self):
		last_entries = self.entries
		self.entries = {}
		f = file(self.filename)
		for line in f.readlines():
			fields = line.strip().split()
			if fields[0][:3].lower() != "cpu":
				continue
			c = cpustat(fields)
			if c.name == "cpu":
				idx = 0
			else:
				idx = int(c.name[3:]) + 1
			self.entries[idx] = c
		f.close()
		last_time = self.time
		self.time = time.time()
		if last_entries:
			delta_sec = self.time - last_time
			interval_hz = delta_sec * self.hertz
			for cpu in self.entries.keys():
				if cpu not in last_entries:
					curr.usage = 0
					continue
				curr = self.entries[cpu]
				prev = last_entries[cpu]
				delta = (curr.user - prev.user) + \
					(curr.nice - prev.nice) + \
					(curr.system - prev.system)
				curr.usage = (delta / interval_hz) * 100
				if curr.usage > 100:
					curr.usage = 100

if __name__ == '__main__':
	import sys

	ints = interrupts()

	for i in ints.interrupts.keys():
		print "%s: %s" % (i, ints.interrupts[i])

	options = cmdline()
	for o in options.options.keys():
		print "%s: %s" % (o, options.options[o])

	cpu = cpuinfo()
	print "\ncpuinfo data: %d processors" % cpu.nr_cpus
	for tag in cpu.keys():
		print "%s=%s" % (tag, cpu[tag])

	print "smaps:\n" + ("-" * 40)
	s = smaps(int(sys.argv[1]))
	for i in range(s.nr_entries):
		print "%#x %s" % (s.entries[i].vm_start, s.entries[i].name)
	print "-" * 40
	for a in s.find_by_name_fragment(sys.argv[2]):
		print a["Size"]

	ps = pidstats()
	print ps[1]

	cs = cpusstats()
	while True:
		time.sleep(1)
		cs.reload()
		for cpu in cs:
			print "%s: %d" % (cpu.name, cpu.usage)
		print "-" * 10
