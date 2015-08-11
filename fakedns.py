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

import argparse,socket,os
import daemon.runner
from twisted.internet import reactor, defer, threads
from twisted.names import client, dns, error, server

class DynamicResolver(object):
    def __init__(self, suffix = None):
        self.suffix = suffix

    def gethostbyname(self, name):
        try:
            address = socket.gethostbyname(name if self.suffix is None else name + self.suffix)
            answer = dns.RRHeader(name=name,payload=dns.Record_A(address=address),ttl=15)
            return ([answer],[],[])
        except socket.gaierror:
            raise error.DomainError()

    def query(self, query, timeout=None):
        if query.type == dns.A:
            return threads.deferToThread(self.gethostbyname, query.name.name)
        #else
        return defer.fail(error.DomainError())

def run(suffix = None, port = 53, bind_address="127.0.0.1"):
    factory = server.DNSServerFactory(clients=[DynamicResolver(suffix)])
    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(port, protocol, interface=bind_address)
    reactor.listenTCP(port, factory, interface=bind_address)

    reactor.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", type=str, help="Name suffix added when resolve")
    parser.add_argument("-p", "--port", type=int, default=53 if os.getuid() == 0 else 10053, help="Port number to listen")
    parser.add_argument("-a", "--bind-address", type=str, default="127.0.0.1", help="Bind address")
    args = parser.parse_args()

    run(args.suffix, args.port, args.bind_address)
