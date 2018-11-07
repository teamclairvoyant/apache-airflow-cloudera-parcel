#!/usr/bin/python
# Copyright (c) 2013, Red Hat, Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of Red Hat nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors:  Stanislav Ochotnicky <sochotnicky@redhat.com>
import gzip
import os.path

from lxml.etree import fromstring

from javapackages.artifact import Artifact

class DepmapLoadingException(Exception):
    pass

class DepmapInvalidException(Exception):
    pass

class Depmap(object):
    """
    Class for working with depmap files (dependency maps). These are files used
    by XMvn to provide mapping between Maven artifacts and file on the
    filesystem.

    Example usage:
    >>> d = Depmap('maven-idea-plugin.xml')
    >>> print d.get_java_requires()
    1.5
    >>> print d.get_provided_artifacts()[0]
    org.apache.maven.plugins:maven-idea-plugin:None:None:2.2
    """

    def __init__(self, path):
        self.__path = path
        self.__load_depmap(path)
        if self.__doc is None:
            raise DepmapLoadingException("Failed to load fragment {path} You have a problem".format(path=path))
        if not self.get_provided_mappings():
            raise DepmapLoadingException("Depmap {path} does not contain any provided artifacts ".format(path=path))

    def __load_depmap(self, fragment_path):
        with open(fragment_path) as f:
            try:
                gzf = gzip.GzipFile(os.path.basename(fragment_path),
                                    'rb',
                                    fileobj=f)
                data = gzf.read()
            except IOError:
                # not a compressed fragment, just rewind and read the data
                f.seek(0)
                data = f.read()

            self.__doc = fromstring(data)


    def is_compat(self):
         """Return true if depmap is for compatibility package

         This means package should have versioned provides"""

         provided_maps = self.get_provided_mappings()
         for m, l in provided_maps:
             if l.version:
                 return True
         return self.__doc.find(".//skipProvides") is not None

    def get_provided_artifacts(self):
        """Returns list of Artifact provided by given depmap."""
        artifacts = []
        for dep in self.__doc.findall('.//dependency'):
            artifact = dep.findall('./maven')
            if len(artifact) != 1:
                raise DepmapInvalidException("Multiple maven nodes in dependency")
            artifact = Artifact.from_xml_element(artifact[0])
            if not artifact.version:
                raise DepmapInvalidException("Depmap {path} does not have version in maven provides".format(path=self.__path))
            artifacts.append(artifact)
        return artifacts

    def get_provided_mappings(self):
        """Return list of (Artifact, Artifact) tuples.

        First part of returned tuple is Maven artifact identification
        Second part of returned tuple is local artifact identification
        """
        mappings = []
        for dep in self.__doc.findall('.//dependency'):
            m_artifact = dep.findall('./maven')
            if len(m_artifact) != 1:
                raise DepmapInvalidException("Multiple maven nodes in dependency")
            m_artifact = Artifact.from_xml_element(m_artifact[0])
            if not m_artifact.version:
                raise DepmapInvalidException("Depmap {path} does not have version in maven provides".format(path=self.__path))
            l_artifact = dep.findall('./jpp')
            if len(l_artifact) != 1:
                raise DepmapInvalidException("Multiple jpp nodes in dependency")
            l_artifact = Artifact.from_xml_element(l_artifact[0])
            mappings.append((m_artifact, l_artifact))
        return mappings

    def get_required_artifacts(self):
        """Returns list of Artifact required by given depmap."""
        artifacts = []
        for dep in self.__doc.findall('.//autoRequires'):
            artifact = Artifact.from_xml_element(dep)
            artifacts.append(artifact)
        return artifacts

    def get_skipped_artifacts(self):
        """Returns list of Artifact that were build but not installed"""
        artifacts = []
        for dep in self.__doc.findall('.//skippedArtifact'):
            artifact = Artifact.from_xml_element(dep)
            artifacts.append(artifact)
        return artifacts

    def get_java_requires(self):
        """Returns JVM version required by depmap or None"""
        jreq = self.__doc.find('.//requiresJava')
        if jreq is not None:
            jreq = jreq.text
        return jreq

    def get_java_devel_requires(self):
        """Returns JVM development version required by depmap or None"""
        jreq = self.__doc.find('.//requiresJavaDevel')
        if jreq is not None:
            jreq = jreq.text
        return jreq
