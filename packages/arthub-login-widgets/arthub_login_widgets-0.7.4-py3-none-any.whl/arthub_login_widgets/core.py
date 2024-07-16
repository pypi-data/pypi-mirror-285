# -*- coding: utf-8 -*-
"""A Qt Widget for login ArtHub."""

# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Import built-in modules
import logging
import webbrowser
import os
import re

# Import third-party modules
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from arthub_api import OpenAPI
from arthub_api import api_config_qq
from arthub_api import api_config_qq_test

# Import local modules
from arthub_login_widgets.constants import ARTHUB_RESET_PASSWORD_WEB_URL
from arthub_login_widgets.constants import ARTHUB_SET_ACCOUNT_INFO_WEB_URL
from arthub_login_widgets.constants import UI_TEXT_MAP
from arthub_login_widgets.filesystem import get_login_account
from arthub_login_widgets.filesystem import get_resource_file
from arthub_login_widgets.filesystem import get_client_exe_path
from arthub_login_widgets.filesystem import save_login_account
from arthub_login_widgets.filesystem import get_token_from_file
from arthub_login_widgets.filesystem import run_exe_sync
from arthub_login_widgets.filesystem import ProcessRunner
from arthub_login_widgets.exception import ErrorClientNotExists


def load_style_sheet(style_file):
    with open(style_file, "r") as css_file:
        css_string = css_file.read().strip("\n")
        data = os.path.expandvars(css_string)
        return data


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(
            self,
            api,
            api_callback=None,
            parent_window=None,
            language_cn=True,
            save_login_state=True
    ):
        """Initialize an instance.

        Args:
            api(arthub_api.OpenAPI): The instance of the arthub_api.OpenAPI.
            api_callback (Function, optional): Called when the login is successful, the login status will be saved
                                                     in arthub_open_api.
            parent_window (QtWidgets.QWidget, optional): The Qt main window instance.
            language_cn (Boolean, optional): The text is displayed in Chinese, otherwise in English.

        """
        super(LoginWindow, self).__init__(parent=parent_window)
        self.language_cn = language_cn
        self.arthub_open_api = api
        self._api_callback = api_callback
        self.callback_return = None
        self.logged = False
        self.login_account_info = None
        self.save_login_state = save_login_state

        # init ui
        self.setFixedSize(300, 300)
        self.central_widget = QtWidgets.QWidget(self)
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)

        # icon
        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setFixedSize(QtCore.QSize(167, 40))
        self.icon_label.setPixmap(QtGui.QPixmap(get_resource_file("arthub_white.png")))
        self.icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setScaledContents(True)

        # line edit
        def _create_line_edit():
            _line_edit_font = QtGui.QFont()
            _line_edit_font.setPixelSize(13)
            _line_edit = QtWidgets.QLineEdit(self)
            _line_edit.setFont(_line_edit_font)
            _line_edit.setFixedSize(238, 32)
            _line_edit.setTextMargins(5, 0, 5, 0)
            return _line_edit

        self.line_edit_account = _create_line_edit()
        self.line_edit_password = _create_line_edit()
        self.line_edit_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        # login status prompt
        _label_prompt_font = QtGui.QFont()
        _label_prompt_font.setPixelSize(11)
        self.label_prompt = QtWidgets.QLabel("", self)
        self.label_prompt.setObjectName("label_prompt")
        self.label_prompt.setFixedHeight(29)
        self.label_prompt.setFont(_label_prompt_font)
        self.label_prompt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # set account info button+text
        _label_button_font = QtGui.QFont()
        _label_button_font.setPixelSize(11)
        self.button_set_account_info = QtWidgets.QPushButton("click", self)
        self.button_set_account_info.setObjectName("button_set_account_info")
        self.button_set_account_info.setFont(_label_button_font)
        self.button_set_account_info.setFixedWidth(30)
        self.button_set_account_info.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.button_set_account_info.clicked.connect(self.on_set_account_info)

        self.text_set_account_info = QtWidgets.QLabel("to complete personal information", self)
        self.text_set_account_info.setObjectName("text_set_account_info")
        self.text_set_account_info.setFont(_label_prompt_font)

        self.set_account_area = QtWidgets.QWidget(self)
        self.set_account_area.setObjectName("set_account_area")
        set_account_area_layout = QtWidgets.QHBoxLayout(self.set_account_area)
        set_account_area_layout.addWidget(self.button_set_account_info)
        set_account_area_layout.addWidget(self.text_set_account_info)

        # login button
        self.pushButton_login = QtWidgets.QPushButton(self.central_widget)
        self.pushButton_login.setObjectName("pushButton_login")
        self.pushButton_login.setText("")
        self.pushButton_login.setFixedSize(238, 34)
        self.pushButton_login.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.pushButton_login.clicked.connect(self.on_login)

        # reset password button
        self.label_forgot_password = QtWidgets.QPushButton("", self)
        self.label_forgot_password.setObjectName("label_forgot_password")
        self.label_forgot_password.setFont(_label_button_font)
        self.label_forgot_password.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.label_forgot_password.clicked.connect(self.on_forgot_password)

        main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        main_layout.addSpacing(31)
        main_layout.setSpacing(3)
        main_layout.addWidget(self.icon_label)
        main_layout.addSpacing(15)
        main_layout.setAlignment(self.icon_label, QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.line_edit_account)
        main_layout.setAlignment(self.line_edit_account, QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(3)
        main_layout.addWidget(self.line_edit_password)
        main_layout.setAlignment(self.line_edit_password, QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label_prompt)
        main_layout.setAlignment(self.label_prompt, QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.set_account_area)
        main_layout.setAlignment(self.set_account_area, QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.pushButton_login)
        main_layout.setAlignment(self.pushButton_login, QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(1)
        main_layout.addWidget(self.label_forgot_password)
        main_layout.setAlignment(self.label_forgot_password, QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(23)
        self.central_widget.setLayout(main_layout)
        self.translate_ui()

        # init model
        last_account = get_login_account()
        if last_account is not None:
            self.line_edit_account.setText(last_account)

        # set style
        qss_file = get_resource_file("style.qss")
        style_sheet = load_style_sheet(qss_file)
        self.setStyleSheet(style_sheet)

        # init status
        self.show_prompt("")

    def set_callback(self, callback):
        self._api_callback = callback

    def _get_ui_text_by_language(self, key):
        v = UI_TEXT_MAP.get(key)
        if v is None:
            return ""
        return v[1 if self.language_cn else 0]

    def translate_ui(self):
        self.setWindowTitle(self._get_ui_text_by_language("window_title"))
        self.line_edit_account.setPlaceholderText(self._get_ui_text_by_language("account_placeholder"))
        self.line_edit_password.setPlaceholderText(self._get_ui_text_by_language("password_placeholder"))
        self.pushButton_login.setText(self._get_ui_text_by_language("login_button"))
        self.label_forgot_password.setText(self._get_ui_text_by_language("forgot_password_button"))

    def show_prompt(self, text):
        self.set_account_area.setVisible(False)
        self.label_prompt.setVisible(True)
        self.label_prompt.setText(text)

    def show_set_account_info(self):
        self.set_account_area.setVisible(True)
        self.label_prompt.setVisible(False)

    def _on_login_succeeded(self, account):
        save_login_account(account)
        if self._api_callback:
            self.callback_return = self._api_callback(self)
        if self.save_login_state:
            self.arthub_open_api.save_token_to_cache()
        self.logged = True
        self.close()

    def check_account_info(self):
        res = self.arthub_open_api.get_account_detail()
        if not res.is_succeeded():
            self.show_prompt("Account information not found")
            return False
        self.login_account_info = res.first_result()
        company = self.login_account_info.get("company")
        if not company:
            self.show_set_account_info()
            return False
        return True

    def login(self):
        self.show_prompt("")
        account = self.line_edit_account.text()
        password = self.line_edit_password.text()
        if account == "":
            self.show_prompt("Email/Phone cannot be empty")
            return
        if password == "":
            self.show_prompt("Password cannot be empty")
            return
        res = self.arthub_open_api.login(account, password, save_token_to_cache=False)
        if not res.is_succeeded():
            error_msg = res.error_message()
            logging.warning("Log in ArtHub failed: %s", error_msg)
            self.show_prompt(error_msg)
            return
        if self.check_account_info():
            self._on_login_succeeded(account)

    def on_login(self):
        self.login()

    @staticmethod
    def on_forgot_password():
        webbrowser.open(ARTHUB_RESET_PASSWORD_WEB_URL)

    def on_set_account_info(self):
        if self.login_account_info:
            account_name = self.login_account_info.get("account_name")
            webbrowser.open(ARTHUB_SET_ACCOUNT_INFO_WEB_URL + account_name)


class TaskPadWindow(ProcessRunner):
    def __init__(self,
                 login_backend,
                 port_id,
                 window_x=None,
                 window_y=None
                 ):
        self.login_backend = login_backend
        args = login_backend.get_args(window_x=window_x, window_y=window_y, ipc_port=port_id)
        args.append("--taskpad")
        super(TaskPadWindow, self).__init__(exe_path=login_backend.exe_path, args=args)

    def open(self):
        self.start_process()

    def close(self):
        self.stop_process()


class LoginBackend(object):
    def __init__(
            self,
            terminal_type="default",
            business_type="default",
            dev_mode=False,
            exe_path=None
    ):
        r"""
        The following characters cannot be used in the terminal_type and business_type strings:
            - Space
            - " # $ % & ' ( ) + , / : ; < = > ? @ [ \ ] ^ { | } ~
        """
        self.terminal_type = terminal_type
        self.business_type = business_type
        self.dev_mode = dev_mode
        self._last_token = None
        self._account_detail = None
        self._exe_path = get_client_exe_path()
        self._did_logged_out = False
        if exe_path:
            self._exe_path = exe_path
        default_api_config = api_config_qq_test if dev_mode else api_config_qq
        self.open_api = OpenAPI(config=default_api_config,
                                get_token_from_cache=False,
                                api_config_name=None,
                                apply_blade_env=False)
        self.check_exe()

    @property
    def exe_path(self):
        return self._exe_path

    @property
    def token(self):
        return self._last_token

    @property
    def account_detail(self):
        return self._account_detail

    @property
    def token_cache_file_path(self):
        appdata_path = os.getenv('APPDATA')
        return os.path.join(appdata_path, 'arthub-tools', self.business_type, self.terminal_type, "token_cache.yml")

    def base_url(self):
        return self.open_api.base_url()

    def check_exe(self):
        if not os.path.exists(self.exe_path):
            raise ErrorClientNotExists()

    def get_token_from_cache(self):
        return get_token_from_file(self.token_cache_file_path)

    def clear_token_cache(self):
        file_path = self.token_cache_file_path
        if os.path.exists(file_path):
            os.remove(file_path)

    def is_login(self):
        if self._check_local_token_cache():
            return True
        if self._check_blade_env():
            return True
        return False

    def popup_task_pad(self, port_id, window_x=None, window_y=None):
        w = TaskPadWindow(login_backend=self, port_id=port_id)
        w.open()
        return w

    def popup_login(self, window_x=None, window_y=None):
        args = self.get_args(window_x=window_x, window_y=window_y)
        r = self._call_exe(args)
        if not r[0]:
            return False
        return bool(r[1])

    def popup_admin(self, window_x=None, window_y=None):
        args = self.get_args(window_x=window_x, window_y=window_y)
        args.append("--admin")
        r = self._call_exe(args)
        return r[0]

    def popup_introduction(self, window_x=None, window_y=None):
        args = self.get_args(window_x=window_x, window_y=window_y)
        args.append("--introduction")
        r = self._call_exe(args)
        return r[0]

    def get_args(self, window_x=None, window_y=None, ipc_port=None):
        args = [
            "--terminal-type={}".format(self.terminal_type),
            "--business-type={}".format(self.business_type)
        ]
        if self.dev_mode:
            args.append("--dev-mode")
        if (window_x is not None) and (window_y is not None):
            args.append("--window-center-x={}".format(window_x))
            args.append("--window-center-y={}".format(window_y))
        if ipc_port is not None:
            args.append("--ipc-port={}".format(ipc_port))
        return args

    def _call_exe(self, args):
        exit_code, stdout = run_exe_sync(self._exe_path, args)
        match = re.search(r'\[GetArtHubToken\]\s*([^\n]+)', stdout)
        if not match:
            return True, None
        if not self._check_local_token_cache():
            return True, None
        return True, self.token

    def logout(self):
        self.clear_token_cache()
        self._on_logout()

    def _on_logout(self):
        self._last_token = None
        self._account_detail = None
        self.open_api.logout()
        self._did_logged_out = True

    def _check_blade_env(self):
        if self._did_logged_out:
            return False
        open_api = OpenAPI(config=None,
                           get_token_from_cache=False,
                           api_config_name=None,
                           apply_blade_env=True)
        return self._check_open_api(open_api)

    def _check_local_token_cache(self):
        token_data = self.get_token_from_cache()
        if not token_data:
            return False
        # token_data: {"api_token": "xx", "api_env": "qq" or "qq_test" or "public"}
        token = token_data.get("api_token")
        if not token:
            return False
        api_env = token_data.get("api_env") or "qq"
        open_api = OpenAPI(config=None,
                           get_token_from_cache=False,
                           api_config_name=api_env,
                           apply_blade_env=False
                           )
        open_api.set_token(token, False)
        return self._check_open_api(open_api)

    def _check_open_api(self, open_api):
        if not open_api.config or not open_api.token:
            return False
        account_detail = open_api.current_account_info
        if account_detail is None:
            return False

        self.open_api = open_api
        self._account_detail = account_detail
        self._last_token = open_api.token
        return True
