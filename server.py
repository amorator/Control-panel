#! /usr/share/env/bin/python

from flask import (
    render_template,
    url_for,
    request,
    send_from_directory,
    redirect,
    session,
    abort,
)
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime as dt
from datetime import timedelta as td
from os import path, rename, remove, mkdir, listdir
from subprocess import Popen
from re import search
from hashlib import md5

from classes.user import User
from modules.server import Server
from modules.threadpool import ThreadPool


app = Server(path.dirname(path.realpath(__file__)))
# tp = ThreadPool(int(app._sql.config['videos']['max_threads']))


def hash(s):
    return md5(s.encode("utf-8")).hexdigest()


#############################################################
#   404   401   403   500   421     413


@app.errorhandler(401)
def unautorized(e):
    session["redirected_from"] = request.url
    return redirect(url_for("login"))


@app.errorhandler(403)
def forbidden(e):
    return redirect(request.referrer if request.referrer != None else "/")


@app.errorhandler(404)
def not_found(e):
    return redirect(request.referrer if request.referrer != None else "/")


@app.errorhandler(405)
def method_not_allowed(e):
    return redirect("/")


@app.errorhandler(413)
def too_large(e):
    return f"Слишком большой файл {e}!", 403


@app.errorhandler(500)
def internal_server_error(e):
    return f"Ошибка сервера {e}! Сообщите о проблемме 21-00 (ОАСУ).", 500


##############################################################


@app.login_manager.user_loader
def load_user(id):
    user = app._sql.user_by_id([id])
    if user and not user.is_enabled():
        return None
    return user


@app.login_manager.unauthorized_handler
def unauthorized_handler():
    session["redirected_from"] = request.url
    return redirect(url_for("login"))


################################################################


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == "GET":
        return render_template("login.html")
    user = app._sql.user_by_login([request.form["login"]])
    if not user:
        app.flash_error("Пользователь не найден!")
        return render_template("login.html")
    if not user.is_enabled():
        app.flash_error("Пользователь откючен!")
        return render_template("login.html")
    if app.hash(request.form["password"]) != user.password:
        app.flash_error("Неверное имя пользователя или пароль!")
        return render_template("login.html")
    login_user(user)
    return redirect(
        session["redirected_from"] if "redirected_from" in session.keys() else "/"
    )


@app.route("/logout")
def logout():
    logout_user()
    if session.get("was_once_logged_in"):
        del session["was_once_logged_in"]
    return redirect("/")


@app.route("/theme")
def theme():
    if "theme" in session.keys():
        session["theme"] = (session["theme"] + 1) % (
            len(listdir("static/css/themes")) - 1
        )
    else:
        session["theme"] = 1
    return redirect(request.referrer)


#######################################################################


@app.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated == False:
        return redirect("/login")
    return render_template("index.html")


############################################################


@app.route("/usrs", methods=["GET"])
@app.permission_required(1)
def users():
    return render_template("users.html", users=app._sql.user_all())


@app.route("/usrs/add", methods=["POST"])
@app.permission_required(1, "z")
def users_add():
    try:
        name = request.form.get("name")
        login = request.form.get("login")
        if app._sql.user_exists(login, name):
            raise Exception("Пользователь уже существует!")
        app._sql.user_add(
            [
                login,
                name,
                app.hash(request.form.get("password")),
                int(request.form.get("enabled") != None),
                request.form.get("permission"),
            ]
        )
    except Exception as e:
        app.flash_error(e)
    finally:
        return redirect(url_for("users"))


@app.route("/usrs/edit/<id>", methods=["POST"])
@app.permission_required(1, "z")
def users_edit(id):
    try:
        name = request.form.get("name")
        login = request.form.get("login")
        if app._sql.user_exists(login, name, id):
            raise Exception("Имя или логин занято другим пользователем!")
        app._sql.user_edit(
            [
                login,
                name,
                int(request.form.get("enabled") != None),
                request.form.get("permission"),
                id,
            ]
        )
    except Exception as e:
        app.flash_error(e)
    finally:
        return redirect(url_for("users"))


@app.route("/usrs/reset/<id>", methods=["POST"])
@app.permission_required(1, "z")
def users_reset(id):
    try:
        app._sql.user_reset([app.hash(request.form.get("password")), id])
    except Exception as e:
        app.flash_error(e)
    finally:
        return redirect(url_for("users"))


@app.route("/usrs/toggle/<id>", methods=["GET"])
@app.permission_required(1, "z")
def users_toggle(id):
    try:
        app._sql.user_toggle([1 - app._sql.user_by_id([id]).is_enabled(), id])
    except Exception as e:
        app.flash_error(e)
    finally:
        return redirect(url_for("users"))


@app.route("/usrs/delete/<id>", methods=["POST"])
@app.permission_required(1, "z")
def users_delete(id):
    try:
        app._sql.user_delete([id])
    except Exception as e:
        app.flash_error(e)
    finally:
        return redirect(url_for("users"))


#######################################################


@app.route("/vd", methods=["GET"])
@app.permission_required(2)
def video():
    return render_template("video.html")


@app.route("/vd_a", methods=["GET"])
@app.permission_required(2, "b")
def video_archive():
    return render_template("video.html")


#######################################################

if __name__ == "__main__":
    app.run_debug()
