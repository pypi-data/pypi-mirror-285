# -*- coding: utf-8 -*-

import logging
import os
import socket
import sys
from threading import Thread


def get_user_path():
    return os.path.expanduser("~")


class IPCSocket(object):
    k_receive_buffer_size = 1024

    def __init__(self):
        self.socket = None
        self.__receive_callback = None

    def __del__(self):
        self.close()

    def set_receive_callback(self, callback=None):
        self.__receive_callback = callback

    def send_message(self, msg):
        if self.socket is None:
            return

        self.socket.send(msg)

    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def read_data(self):
        while True:
            recv_data = bytes()
            while True:
                try:
                    data = self.socket.recv(IPCSocket.k_receive_buffer_size)
                except Exception:
                    self.socket = None
                    return

                if len(data) == 0:
                    self.socket = None
                    return

                recv_data += data
                if len(data) < IPCSocket.k_receive_buffer_size:
                    break

            if self.__receive_callback is not None:
                response = self.__receive_callback(recv_data)
                if response is not None:
                    self.send_message(response)

    def is_connected(self):
        if self.socket is None:
            return False
        try:
            self.socket.getpeername()
        except socket.error:
            return False
        return True


class IPCServer(IPCSocket):
    def __init__(self):
        super(IPCServer, self).__init__()

        self.__listen_socket = None
        self.__accept_thread = None

    def init(self, listen_port=0):
        listen_port = self.__socket_bind(listen_port)
        return listen_port

    def close_server(self):
        self.close()
        if self.__listen_socket is not None:
            self.__listen_socket.close()
            self.__listen_socket = None

    def __socket_bind(self, listen_port):
        if self.__listen_socket is None:
            self.__listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__listen_socket.bind(('127.0.0.1', listen_port))
            self.__listen_socket.listen(5)

            # create accept thread
            if self.__accept_thread is None:
                self.__accept_thread = Thread(target=self.__accept_client)
                self.__accept_thread.start()
        bind_port = self.__listen_socket.getsockname()[1]
        return bind_port

    def __accept_client(self):
        while True:
            try:
                client, addr = self.__listen_socket.accept()
            except OSError as e:
                return

            if self.socket is not None:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket.close()
                except OSError:
                    # socket has been shutdown
                    pass
                finally:
                    self.socket = None

            self.socket = client
            t = Thread(target=self.read_data)
            t.start()
