# -*- coding: utf-8 -*-
from flask import Flask, g, json
import psycopg2
import psycopg2.extras
from Config import Config
import logging
import os.path

app = Flask(__name__)

### CONFIG
# 설정 읽어오기
crr_path = os.path.dirname(os.path.realpath(__file__))
config = Config(os.path.join(crr_path, "GeepsAdminZoneService.cfg"))


### LOGGING
# 로깅 모드 설정
logging.basicConfig(level=eval("logging." + config.log_mode))
LOG_FILE_PATH = os.path.join(crr_path, config.log_file)

# 로깅 형식 지정
# http://gyus.me/?p=418
logger = logging.getLogger("failLogger")
formatter = logging.Formatter('[%(levelname)s] %(asctime)s > %(message)s')
fileHandler = logging.FileHandler(LOG_FILE_PATH)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


### HANGUL
# 한글로 된 인자들을 받을때 오류가 생기지 않게 기본 문자열을 utf-8로 지정
# http://libsora.so/posts/python-hangul/
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


### DATABASE
# Using SQLite 3 with Flask를 참조해 DB 관리 구조를 만듬
# http://flask.pocoo.org/docs/0.10/patterns/sqlite3/#sqlite3
def connect_to_database():
    if config.db_pwd:
        return psycopg2.connect("dbname={} user={} password={}"
                                .format(config.db_database, config.db_user, config.db_pwd))
    else:
        return psycopg2.connect("dbname={} user={}"
                                .format(config.db_database, config.db_user))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False, as_dict=False):
    # 결과를 col_name:value 딕셔너리로 만든다.
    # http://initd.org/psycopg/docs/extras.html
    if as_dict:
        cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
    else:
        cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


### EVENT
@app.route('/test')
def hello():
    return "GeepsAdminZoneService Activated!"


@app.route('/api/get_class1')
def get_class1():
    out_str = None
    try:
        for row in query_db("select distinct class1 from adminzone_meta order by class1", as_dict=True):
            if not out_str:
                out_str = row['class1']
            else:
                out_str += "<br/>" + row['class1']

    except Exception as e:
        print e

    return out_str


if __name__ == '__main__':
    app.run()
