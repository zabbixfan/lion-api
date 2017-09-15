# -*- coding: utf-8 -*-
import logging
import os
from datetime import timedelta



class Config_Dev(object):
    APP_ID = 
    APP_SECRET = 
    AUTH_SERVER_HOST = "
    AUTH_SERVER_LOGIN_URL = 
    AUTH_SERVER_LOGOUT_URL = 
    SQLALCHEMY_DATABASE_URI = 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 5
    SQLALCHEMY_ECHO = False
    CMDB_URL = 
    ID_TOKEN_DEFAULT_EXPIRES = 8640000
    ACCESS_TOKEN_DEFAULT_EXPIRES = 86400
    CORS_ORIGINS = []

    SONAR_URL = 
    CODEHUB_TOKEN = '
    CODEHUB_URL = 
    GITHOOK_URL = 
    EMALL_SMTP_HOST = 
    EMALL_SMTP_PORT = 465
    EMALL_USER = 
    EMALL_PASSWORD = 
    EMALL_RECEIVERS = []
    SWAGGER = {
        'uiversion': 2,
        'title': 'GitManager',
        'description': 'Gitlab Api Doc',
        "version": "0.0.1"
    }
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_IGNORE_RESULT = True
    CELERY_BROKER_URL = 
    CELERY_RESULT_BACKEND = 

    DEBUG = True
class Config_Ga(Config_Dev):
    SQLALCHEMY_DATABASE_URI = 
    AUTH_SERVER_HOST = 
    AUTH_SERVER_LOGIN_URL = 
    AUTH_SERVER_LOGOUT_URL = 
    ID_TOKEN_DEFAULT_EXPIRES = 8640000
    ACCESS_TOKEN_DEFAULT_EXPIRES = 86400
    CORS_ORIGINS = ['']
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_IGNORE_RESULT = True
    CELERY_BROKER_URL = 
    CELERY_RESULT_BACKEND = 
    CELERYBEAT_SCHEDULE = {
        'syncSearchCodeStatus': {
            'task': 'app.tasks.syncTasks.syncSearchCodeStatus',
            'schedule': timedelta(seconds=60)
        },
    }
    GITHOOK_URL = 
    SONAR_URL = 
    DEBUG = False


Config = Config_Dev

if os.environ.get('ENV_CODE') == "GA":
    Config = Config_Ga
