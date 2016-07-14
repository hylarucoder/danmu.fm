#!/usr/bin/env python
# encoding: utf-8

#!/usr/bin/env python
# encoding: utf-8

'''
静态配置
'''
import logging
from logging.config import dictConfig
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
import sys
import os
import shutil
from sqlalchemy.orm import sessionmaker
from os.path import expanduser

VERSION               = "0.3.0"
PROJECT_NAME          = "danmufm"
MODULE_NAME           = PROJECT_NAME.lower()
# 项目根目录
ROOT_PROJECT_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 项目次目录
MODULE_DIR            = os.path.join(ROOT_PROJECT_DIR, MODULE_NAME)
TEST_DIR              = os.path.join(ROOT_PROJECT_DIR, 'test')
TEMPLATE_DIR          = os.path.join(MODULE_DIR, 'template')

CURRENT_USER_HOME_DIR = expanduser("~")
USER_CONFIG_DIR       = os.path.join(CURRENT_USER_HOME_DIR, '.danmu.fm')
REPORTS_DIR           = os.path.join(USER_CONFIG_DIR, 'reports')
LOGS_DIR              = os.path.join(USER_CONFIG_DIR, 'logs')

if not os.path.exists(USER_CONFIG_DIR):
    os.makedirs(USER_CONFIG_DIR)

if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# 拷贝模板配置文件
CONFIG_FILE = os.path.join(USER_CONFIG_DIR,"danmu.fm.conf")
if not os.path.exists(CONFIG_FILE):
    shutil.copy(os.path.join(TEMPLATE_DIR,"danmu.fm.conf"),USER_CONFIG_DIR)

config = {}

with open(CONFIG_FILE) as f:
    code = compile(f.read(), CONFIG_FILE, 'exec')
    exec(code, config)
# 数据库配置
USE_SQLITE = config["USE_SQLITE"] # Whether or not to show DEBUG level messages
DATABASE_CONFIG = config["DATABASE_CONFIG"]

# 日志配置
## 开启DEBUG以上
DEBUG = config["DEBUG"] # Whether or not to show DEBUG level messages
## 开启日志颜色
USE_COLORS = config["USE_COLORS"] # Whether or not colors should be used when outputting text

# danmu.client
# danmu.fm 文件即可
LOGGING = {  # dictConfig for output stream and file logging
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'console': {
            'format': '[%(asctime)s] %(levelname)s::%(module)s - %(message)s',
        },
        'file': {
            'format': '[%(asctime)s] %(levelname)s::(P:%(process)d T:%(thread)d)::%(module)s - %(message)s',
        },
    },

    'handlers': {
        'console': {
            'class': MODULE_NAME + '.misc.color_stream_handler.ColorStreamHandler',
            'formatter': 'console',
            'level': 'DEBUG',
            'use_colors': USE_COLORS,
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'file',
            'level': 'INFO',
            'when': 'midnight',
            'filename': str(LOGS_DIR) + '/danmu.fm.log',
            'interval': 1,
            'backupCount': 0,
            'encoding': None,
            'delay': False,
            'utc': False,
        },
    },

    'loggers': {
        'default': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'danmu.client': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
        'danmu.fm': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        }
    }
}
dictConfig(LOGGING)

## 邮件设置

MAIL_SMTP_HOST = config["MAIL_SMTP_HOST"]
MAIL_USER      = config["MAIL_USER"]
MAIL_PASSWORD  = config["MAIL_PASSWORD"]


ENGINE = create_engine(URL(**DATABASE_CONFIG))

SESSION_FACTORY = sessionmaker(bind=ENGINE,echo=DEBUG)

# 检查配置使用,真实环境中应该取消
# print(locals())





# [TODO: 添加设置报告]
