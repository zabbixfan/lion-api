#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, g, request, jsonify
from . import ctl as app
from ..common.alopex_auth_sdk import need_login2, logout
import logging
@app.route("/", methods=["GET"])
@need_login2()
def index():

    return "Hello " + g.user["name"] + " <a href='/logout'>退出</a>"


@app.route("/logout", methods=["GET"])
def user_logout():
    return logout()

