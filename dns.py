#!/usr/bin/env python3

"""
Based from:
https://gist.githubusercontent.com/wmax641/aa50e3bb924e138d94e9/raw/a17c5cf7ef4aa028bf2f680ad9ee7dfc06b16773/dumbdns.py
"""

import datetime
import threading
import socketserver
import urllib.request
import json
import argparse

from dnslib import *

parser = argparse.ArgumentParser(description='Start DNS Service')
parser.add_argument('--port', help="Server port", type=int, default=5053)
parser.add_argument('--ttl', help="Record TTL", type=int, default=30)
parser.add_argument('--registry', help="Service Registry", type=str, default="127.0.0.1:5000")
parser.add_argument('--forward', help="DNS to forward to if not in database", type=str, default="8.8.8.8")
args = parser.parse_args()

LISTENING_PORT = args.port  # Port to listen on
UDP_LISTEN = True  # Listen on UDP?
TCP_LISTEN = True  # Listen on TCP as well?
ALSO_LOG_STDOUT = True  # Print to stdout as well as logging
MAX_LOG_SIZE = 20000
TTL = args.ttl
DNS_FORWARD = args.forward
REGISTRY_HOST = args.registry


class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)


def get_ip_list(qn):
    try:

        req = urllib.request.Request('http://{}/{}'.format(REGISTRY_HOST, qn[:-1]))
        webURL = urllib.request.urlopen(req)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        res = json.loads(data.decode(encoding))

        endpoints = res.keys()
        a_list = [e.split(":")[0] for e in endpoints]
    except Exception:
        return []

    return a_list


def dns_response(request):
    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    a_list = get_ip_list(qn)

    # If domain is found in our own database
    if len(a_list) > 0:
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        if (qtype == 1):
            for a in a_list:
                reply.add_answer(RR(rname=qname, rtype=1, rclass=1, ttl=TTL, rdata=A(a)))
        return reply

    # If not then forward the request to other DNS
    else:

        return None


def dns_alternative_response(request):
    ans_pkt = request.send(DNS_FORWARD)
    return DNSRecord.parse(ans_pkt)


class BaseRequestHandler(socketserver.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        try:
            data = self.get_data()
            request = DNSRecord.parse(data)

            data = dns_response(request)
            if data is None:
                data = dns_alternative_response(request)
            self.send_data(data.pack())
        except Exception as e:
            print("\t|-> Ignoring bad packet ({})".format(str(e)))


class TCPRequestHandler(BaseRequestHandler):

    def get_data(self):
        data = self.request.recv(8192).strip()
        sz = struct.unpack('>H', data[:2])[0]
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data):
        sz = struct.pack('>H', len(data))
        return self.request.sendall(sz + data)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


def startServer():
    servers = []
    if UDP_LISTEN: servers.append(socketserver.ThreadingUDPServer(('', LISTENING_PORT), UDPRequestHandler))
    if TCP_LISTEN: servers.append(socketserver.ThreadingTCPServer(('', LISTENING_PORT), TCPRequestHandler))

    now = datetime.datetime.now().strftime("%a %d-%b %H:%M:%S")
    print("{}: Starting nameserver on port {}\n".format(now, LISTENING_PORT))

    for s in servers:
        thread = threading.Thread(target=s.serve_forever)
        thread.daemon = True  # exit the server thread when the main thread terminates
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.shutdown()


if __name__ == '__main__':
    startServer()
