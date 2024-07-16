# -*- coding: utf-8 -*-
"""The utils functions of the arthub_login_window."""

# Import built-in modules
import os
import re
import subprocess
import threading

# Import third-party modules
import yaml

try:
    # Python 3
    from queue import Queue, Empty
except ImportError:
    # Python 2
    from Queue import Queue, Empty

# Import third-party modules
from platformdirs import user_cache_dir


def current_path():
    return os.path.dirname(__file__)


def get_client_exe_path():
    root = current_path()
    return os.path.join(root, "resources", "client", "arthub-tools.exe")


def get_resource_file(file_name):
    root = current_path()
    return os.path.join(root, "resources", file_name)


def read_file(file_path):
    with open(file_path, "r") as file_obj:
        return file_obj.read()


def write_file(file_path, data):
    with open(file_path, "w") as file_obj:
        file_obj.write(data)


def get_login_account():
    account_file = get_account_cache_file()
    if os.path.exists(account_file):
        return read_file(account_file)


def save_login_account(account, cache_file=None):
    account_file = cache_file or get_account_cache_file()
    write_file(account_file, account)


def get_account_cache_file():
    root = user_cache_dir(appauthor="arthub", opinion=False)
    try:
        os.makedirs(root)
    # Ingoing when try create folder failed.
    except (IOError, WindowsError):
        pass
    return os.path.join(root, "arthub_account")


def run_exe_sync(exe_path, args):
    command = [exe_path] + args
    if hasattr(subprocess, 'run'):
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return result.returncode, result.stdout
    else:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        return process.returncode, stdout


def get_token_from_file(cache_file):
    if not os.path.exists(cache_file):
        return
    with open(cache_file, "r+") as f:
        return yaml.safe_load(f)


class ProcessRunner(object):
    def __init__(self, exe_path, args):
        self.exe_path = exe_path
        self.args = [exe_path] + args
        self.process = None
        self.output = ""
        self.errors = ""
        self.output_queue = Queue()
        self.error_queue = Queue()
        self.closed_callback = None
        # self.stdout_thread = None
        # self.stderr_thread = None

    @staticmethod
    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line.decode())
        out.close()

    def start_process(self):
        self.process = subprocess.Popen(self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # self.stdout_thread = threading.Thread(target=self.enqueue_output, args=(self.process.stdout, self.output_queue))
        # self.stderr_thread = threading.Thread(target=self.enqueue_output, args=(self.process.stderr, self.error_queue))
        # self.stdout_thread.daemon = True
        # self.stderr_thread.daemon = True
        # self.stdout_thread.start()
        # self.stderr_thread.start()

        threading.Thread(target=self._wait_for_exit).start()

    def _wait_for_exit(self):
        self.process.wait()
        if self.closed_callback:
            self.closed_callback()

    def read_output(self):
        try:
            while True:
                self.output += self.output_queue.get_nowait()
        except Empty:
            pass
        try:
            while True:
                self.errors += self.error_queue.get_nowait()
        except Empty:
            pass
        return self.output, self.errors

    def stop_process(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            # self.read_output()

    def on_closed(self, callback):
        self.closed_callback = callback

    def __del__(self):
        self.stop_process()
