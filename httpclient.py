#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle,Yuan Wang https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re

# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    def get_host_port(self, url):
        parse_result = urllib.parse.urlparse(url)
        host = parse_result.hostname
        port = parse_result.port
        path = parse_result.path

        return host, port or 80, path or "/"

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        data_list = data.split("\r\n",1)
        status_line = data_list[0]
        code = int(status_line.split()[1])

        return code

    def get_headers(self, data):
        
        return None

    def get_body(self, data):

        data_list = data.split("\r\n\r\n")
        body = data_list[1]

        return body

    def sendall(self, data):
        self.socket.sendall(data.encode("utf-8"))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode("utf-8")

    def GET(self, url, args=None):
        code = 500
        host, port, path = self.get_host_port(url)
        header = self.buildHeader("GET", path, host)
        request = "{}\r\n\r\n".format(header)
        self.connect(host, port)
        self.sendall(request)
        response = ""
        response += self.recvall(self.socket)
        code, body = self.get_code(response),self.get_body(response)
    

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        host, port, path = self.get_host_port(url)
        header = self.buildHeader("POST", path, host)

        data = "" if args == None else urllib.parse.urlencode(args)
        content_type = "Content-Type: application/x-www-form-urlencoded"
        content_length = "Content-Length: {}".format(len(data))
        request = "{}\r\n{}\r\n{}\r\n\r\n{}".format(header,content_type,content_length,data)

        self.connect(host, port)
        self.sendall(request)

        response = ""
        response += self.recvall(self.socket)
        code, body = self.get_code(response),self.get_body(response)

        self.close()
        return HTTPResponse(code, body)

    def buildHeader(self, method, path, host):
        status_line = "{} {} HTTP/1.1".format(method,path)
        user_agent = "User-Agent: curl/7.64.1"
        accept = "Accept: */*"
        connection = "Connection: close"
        host = "Host: {}".format(host)

        return "\r\n".join([status_line,host,user_agent,accept,connection])

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
