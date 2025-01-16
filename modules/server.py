from flask import Flask, flash, abort
from flask_login import LoginManager, current_user
from flask_cors import CORS
from functools import wraps
from re import sub
from hashlib import md5

from modules.SQLUtils import SQLUtils


class Server(Flask):
    def __init__(self, root, name=__name__):
        super().__init__(name, root_path=root)
        CORS(self, resources={r"*": {"origins": "*"}}, supports_credentials=True)
        self.secret_key = "achudwshoiqxjqi@eowe1J2"
        self.config["TEMPLATES_AUTO_RELOAD"] = True
        self.config["SESSION_TYPE"] = "filesystem"
        self.config["SESSION_PERMANENT"] = True
        self.config["PERMANENT_SESSION_LIFETIME"] = 86400
        self.config["SESSION_COOKIE_HTTPONLY"] = False
        self.config["SESSION_REFRESH_EACH_REQUEST"] = True
        self.init()

    def init(self):
        self.login_manager = LoginManager(self)
        self.login_manager.login_view = "login"
        self.login_manager.login_message = "Please log in to access this page."
        self.login_manager.refresh_view = "reauth"
        self._sql = SQLUtils()

    def run_debug(self):
        self.run(
            host="0.0.0.0",
            port=443,
            ssl_context=("/etc/ssl/.ssl/znv.crt", "/etc/ssl/.ssl/znv.key"),
            threaded=True,
            debug=True,
        )

    def hash(self, s):
        return md5(s.encode("utf-8")).hexdigest()

    def flash_error(self, e):
        msg = sub("['\"]", "", str(e))
        flash(msg)

    def permission_required(self, id, perm="a"):
        def _permission_required(f):
            @wraps(f)
            def wrap(*args, **kwargs):
                if not current_user.is_authenticated:
                    return abort(401)
                if id == 0 or current_user.is_allowed(id, perm):
                    return f(*args, **kwargs)
                else:
                    return abort(403)

            return wrap

        return _permission_required
