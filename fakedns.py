#!/usr/bin/python2.7
'''
The MIT License (MIT)

Copyright (c) 2015 Walbrix Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

# apt-get install python-twisted-names
# emerge twisted-names

import argparse,socket
import daemon.runner
from twisted.internet import reactor, defer
from twisted.names import client, dns, error, server

class DynamicResolver(object):
    def __init__(self, suffix = None):
        self.suffix = suffix

    def query(self, query, timeout=None):
        if query.type == dns.A:
            name = query.name.name
            if self.suffix is not None: name += self.suffix
            try:
                address = socket.gethostbyname(name)
                answer = dns.RRHeader(name=query.name.name,payload=dns.Record_A(address=address),ttl=15)
                return defer.succeed(([answer],[],[]))
            except:
                pass
        #else
        return defer.fail(error.DomainError())

def run(suffix = None):
    factory = server.DNSServerFactory(clients=[DynamicResolver(suffix)])
    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(53, protocol)
    reactor.listenTCP(53, factory)

    reactor.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", type=str, help="Name suffix added when resolve")
    args = parser.parse_args()

    run(args.suffix)
