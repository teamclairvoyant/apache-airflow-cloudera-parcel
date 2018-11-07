#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
certs.py
~~~~~~~~

This module returns the preferred default CA certificate bundle.

If you are packaging Requests, e.g., for a Linux distribution or a managed
environment, you can change the definition of where() to return a separately
packaged CA bundle.

We return "/etc/pki/tls/certs/ca-bundle.crt" provided by the ca-certificates
package.
"""

try:
    from certifi import where
except ImportError:
    def where():
        """ Don't use the certs bundled with requests, use ca-certificates. """
        return "/etc/pki/tls/certs/ca-bundle.crt"

if __name__ == '__main__':
    print(where())
