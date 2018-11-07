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

import re
import sys

from lxml.etree import Element, SubElement, tostring

class ArtifactException(Exception):
    pass

class ArtifactFormatException(ArtifactException):
    pass

class ArtifactValidationException(ArtifactException):
    pass

class Artifact(object):
    """
    Simplified representation of Maven artifact for purpose of packaging

    Package consists mostly of simple properties and string formatting and
    loading functions to prevent code duplication elsewhere
    """

    def __init__(self, groupId, artifactId, extension="",
                 classifier="", version="", namespace=""):
        self.groupId = groupId.strip()
        self.artifactId = artifactId.strip()
        self.extension = extension.strip()
        self.classifier = classifier.strip()
        self.version = version.strip()
        self.namespace = namespace.strip()

    def __unicode__(self):
        return u"{gid}:{aid}:{ext}:{cls}:{ver}".format(gid=self.groupId,
                                                       aid=self.artifactId,
                                                       ext=self.extension,
                                                       cls=self.classifier,
                                                       ver=self.version)

    def __str__(self):
        return unicode(self).encode(sys.getfilesystemencoding())

    def get_rpm_str(self, versioned=False):
        """Return representation of artifact as used in RPM dependencies

        versioned -- return artifact string including version

        Example outputs:
        mvn(commons-logging:commons-logging)
        mvn(commons-logging:commons-logging:1.2) # versioned
        mvn(commons-logging:commons-logging:war:)
        mvn(commons-logging:commons-logging:war:1.2) # versioned
        mvn(commons-logging:commons-logging:war:test-jar:)
        mvn(commons-logging:commons-logging:war:test-jar:1.3) # versioned
        maven31-mvn(commons-logging:commons-logging)
        """
        namespace = "mvn"
        if self.namespace:
            namespace = self.namespace + "-mvn"

        mvnstr = "{gid}:{aid}".format(gid=self.groupId,
                                      aid=self.artifactId)

        if self.extension:
            mvnstr = mvnstr + ":{ext}".format(ext=self.extension)

        if self.classifier:
            if not self.extension:
                mvnstr = mvnstr + ":"
            mvnstr = mvnstr + ":{clas}".format(clas=self.classifier)

        if versioned:
            if not (self.version):
                raise ArtifactFormatException(
                    "Cannot create versioned string from artifact without version: {art}".format(art=str(self)))
            mvnstr = mvnstr + ":{ver}".format(ver=self.version)
        elif self.classifier or self.extension:
            mvnstr = mvnstr + ":"

        return "{namespace}({mvnstr})".format(namespace=namespace,
                                              mvnstr=mvnstr)


    def get_xml_element(self, root="artifact"):
        """
        Return XML Element node representation of the Artifact
        """
        root = Element(root)

        for key in ("artifactId", "groupId", "extension", "version",
                    "classifier", "namespace"):
            if hasattr(self, key) and getattr(self,key):
                item = SubElement(root, key)
                item.text = getattr(self, key)
        return root

    def get_xml_str(self, root="artifact"):
        """
        Return XML formatted string representation of the Artifact
        """
        root = self.get_xml_element(root)
        return tostring(root, pretty_print=True)

    def validate(self, allow_empty=True, allow_wildcards=True, allow_backref=True):
        """
        Function to validate current state of artifact with regards to
        wildcards, empty parts and backreference usage
        """
        all_empty = True
        wildcard_used = False
        backref_used = False
        backref_re = re.compile('@\d+')
        for key in ("artifactId", "groupId", "extension", "version",
                    "classifier", "namespace"):
            val = getattr(self, key)
            if not val:
                continue
            if val:
               all_empty = False
            if val.find('*') != -1:
                wildcard_used = True
            if backref_re.match(val):
                backref_used = True

        if not allow_empty and all_empty:
            raise ArtifactValidationException("All parts of artifact are empty")
        if not allow_wildcards and wildcard_used:
            raise ArtifactValidationException("Wildcard used in artifact")
        if not allow_backref and backref_used:
            raise ArtifactValidationException("Backreference used in artifact")
        return True

    @classmethod
    def merge_artifacts(cls, dominant, recessive):
        """
        Merge two artifacts into one. Information missing in dominant artifact will
        be copied from recessive artifact. Returns new merged artifact
        """
        ret = cls(dominant.groupId, dominant.artifactId, dominant.extension,
                  dominant.classifier, dominant.version, dominant.namespace)
        for key in ("artifactId", "groupId", "extension", "version",
                    "classifier", "namespace"):
            if not getattr(ret, key):
                setattr(ret, key, getattr(recessive, key))
        return ret

    @classmethod
    def from_xml_element(cls, xmlnode, namespace=""):
        """
        Create Artifact from xml.etree.ElementTree.Element as contained
        within pom.xml or a dependency map.
        """
        parts = {'groupId':'',
                 'artifactId':'',
                 'extension':'',
                 'classifier':'',
                 'version':''}

        for key in parts:
            node = xmlnode.find("./" + key)
            if node is not None and node.text is not None:
                parts[key] = node.text.strip()

        if not parts['groupId'] or not parts['artifactId']:
            raise ArtifactFormatException(
                "Empty groupId or artifactId encountered. "
                "This is a bug, please report it!")


        if not namespace:
            namespace = xmlnode.find('./namespace')
            if namespace is not None:
                namespace = namespace.text.strip()
            else:
                namespace = ""

        return cls(parts['groupId'], parts['artifactId'], parts['extension'],
                   parts['classifier'], parts['version'], namespace)

    @classmethod
    def from_mvn_str(cls, mvnstr, namespace=""):
        """
        Create Artifact from Maven-style definition

        The string should be in the format of:
           groupId:artifactId[:extension[:classifier]][:version]

        Where last part is always considered to be version unless empty
        """
        tup = mvnstr.split(":")

        # groupId and artifactId are always present
        if len(tup) < 2:
            raise ArtifactFormatException("Artifact string '{mvnstr}' does not "
                                          "contain ':' character. Can not parse".format(mvnstr=mvnstr))

        if len(tup) > 5:
            raise ArtifactFormatException("Artifact string '{mvnstr}' contains "
                                          "too many colons. Can not parse".format(mvnstr=mvnstr))

        groupId = tup[0]
        artifactId = tup[1]
        extension = tup[2] if len(tup) >= 4 else ""
        classifier = tup[3] if len(tup) >= 5 else ""
        version = tup[-1] if len(tup) >= 3 else ""

        return cls(groupId, artifactId, extension,
                   classifier, version, namespace)
