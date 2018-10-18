import sys, os, socket, atexit, re
import pkg_resources
from pkg_resources import ResolutionError, ExtractionError
from setuptools.compat import urllib2

try:
    import ssl
except ImportError:
    ssl = None

__all__ = [
    'VerifyingHTTPSHandler', 'find_ca_bundle', 'is_available', 'cert_paths',
    'opener_for'
]

cert_paths = """
/etc/pki/tls/certs/ca-bundle.crt
/etc/ssl/certs/ca-certificates.crt
/usr/share/ssl/certs/ca-bundle.crt
/usr/local/share/certs/ca-root.crt
/etc/ssl/cert.pem
/System/Library/OpenSSL/certs/cert.pem
""".strip().split()


HTTPSHandler = HTTPSConnection = object

for what, where in (
    ('HTTPSHandler', ['urllib2','urllib.request']),
    ('HTTPSConnection', ['httplib', 'http.client']),
):
    for module in where:
        try:
            exec("from %s import %s" % (module, what))
        except ImportError:
            pass

is_available = ssl is not None and object not in (HTTPSHandler, HTTPSConnection)





try:
    from socket import create_connection
except ImportError:
    _GLOBAL_DEFAULT_TIMEOUT = getattr(socket, '_GLOBAL_DEFAULT_TIMEOUT', object())
    def create_connection(address, timeout=_GLOBAL_DEFAULT_TIMEOUT,
                          source_address=None):
        """Connect to *address* and return the socket object.

        Convenience function.  Connect to *address* (a 2-tuple ``(host,
        port)``) and return the socket object.  Passing the optional
        *timeout* parameter will set the timeout on the socket instance
        before attempting to connect.  If no *timeout* is supplied, the
        global default timeout setting returned by :func:`getdefaulttimeout`
        is used.  If *source_address* is set it must be a tuple of (host, port)
        for the socket to bind as a source address before making the connection.
        An host of '' or port 0 tells the OS to use the default.
        """
        host, port = address
        err = None
        for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)
                if timeout is not _GLOBAL_DEFAULT_TIMEOUT:
                    sock.settimeout(timeout)
                if source_address:
                    sock.bind(source_address)
                sock.connect(sa)
                return sock

            except error:
                err = True
                if sock is not None:
                    sock.close()
        if err:
            raise
        else:
            raise error("getaddrinfo returns an empty list")


from backports.ssl_match_hostname import CertificateError, match_hostname
























class VerifyingHTTPSHandler(HTTPSHandler):
    """Simple verifying handler: no auth, subclasses, timeouts, etc."""

    def __init__(self, ca_bundle):
        self.ca_bundle = ca_bundle
        HTTPSHandler.__init__(self)

    def https_open(self, req):
        return self.do_open(
            lambda host, **kw: VerifyingHTTPSConn(host, self.ca_bundle, **kw), req
        )


class VerifyingHTTPSConn(HTTPSConnection):
    """Simple verifying connection: no auth, subclasses, timeouts, etc."""
    def __init__(self, host, ca_bundle, **kw):
        HTTPSConnection.__init__(self, host, **kw)
        self.ca_bundle = ca_bundle

    def connect(self):
        sock = create_connection(
            (self.host, self.port), getattr(self,'source_address',None)
        )

        # Handle the socket if a (proxy) tunnel is present
        if hasattr(self, '_tunnel') and getattr(self, '_tunnel_host', None):
            self.sock = sock
            self._tunnel()
            # http://bugs.python.org/issue7776: Python>=3.4.1 and >=2.7.7
            # change self.host to mean the proxy server host when tunneling is
            # being used. Adapt, since we are interested in the destination
            # host for the match_hostname() comparison.
            actual_host = self._tunnel_host
        else:
            actual_host = self.host

        self.sock = ssl.wrap_socket(
            sock, cert_reqs=ssl.CERT_REQUIRED, ca_certs=self.ca_bundle
        )
        try:
            match_hostname(self.sock.getpeercert(), actual_host)
        except CertificateError:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            raise

def opener_for(ca_bundle=None):
    """Get a urlopen() replacement that uses ca_bundle for verification"""
    return urllib2.build_opener(
        VerifyingHTTPSHandler(ca_bundle or find_ca_bundle())
    ).open



_wincerts = None

def get_win_certfile():
    global _wincerts
    if _wincerts is not None:
        return _wincerts.name

    try:
        from wincertstore import CertFile
    except ImportError:
        return None

    class MyCertFile(CertFile):
        def __init__(self, stores=(), certs=()):
            CertFile.__init__(self)
            for store in stores:
                self.addstore(store)
            self.addcerts(certs)
            atexit.register(self.close)

    _wincerts = MyCertFile(stores=['CA', 'ROOT'])
    return _wincerts.name


def find_ca_bundle():
    """Return an existing CA bundle path, or None"""
    if os.name=='nt':
        return get_win_certfile()
    else:
        for cert_path in cert_paths:
            if os.path.isfile(cert_path):
                return cert_path
    try:
        return pkg_resources.resource_filename('certifi', 'cacert.pem')
    except (ImportError, ResolutionError, ExtractionError):
        return None





