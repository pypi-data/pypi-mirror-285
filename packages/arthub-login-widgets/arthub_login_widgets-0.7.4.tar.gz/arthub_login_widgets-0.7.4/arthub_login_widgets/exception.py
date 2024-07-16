"""
arthub_login_window.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of exceptions.
"""


class Error(Exception):
    """There was an ambiguous exception that occurred while call each interface.
    """

    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return str(self.value)


class ErrorNotLogin(Error):
    def __init__(self):
        Error.__init__(self, value="not login in")


class ErrorClientNotExists(Error):
    def __init__(self):
        Error.__init__(self, value="arthub-tools.exe is not exists")
