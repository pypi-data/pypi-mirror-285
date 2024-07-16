# Import built-in modules
import os

# Import local modules
from arthub_login_widgets.filesystem import get_account_cache_file
from arthub_login_widgets.filesystem import get_login_account
from arthub_login_widgets.filesystem import read_file
from arthub_login_widgets.filesystem import save_login_account


def test_write_last_login_account(tmpdir):
    account_file = tmpdir.join("mytext.aaaaa")
    save_login_account("myaccount", cache_file=str(account_file))
    assert read_file(str(account_file)) == "myaccount"


def test_read_last_login_account():
    file_path = get_account_cache_file()
    if os.path.exists(file_path):
        # Ensure the cache file not exists.
        os.remove(file_path)
    assert get_login_account() is None
