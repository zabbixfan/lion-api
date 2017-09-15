#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api
ctl = Blueprint('ctl', __name__,template_folder='templates',static_folder="static",static_url_path='/app/controllers/static')

api=Api(prefix="/api")

import index
import branches,tags,user,hook,projects
