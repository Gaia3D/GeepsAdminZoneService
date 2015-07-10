# -*- coding: utf-8 -*-
from flask import Flask, g, json, render_template, Response
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
logger = logging.getLogger("AdminZone")
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
        logger.info("### DB CONNECTED.")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        logger.info("### DB DISCONNECTED.")


def query_db(query, args=(), one=False, cursor_factory=None):
    logger.debug(query)
    try:
        if cursor_factory:
            cur = get_db().cursor(cursor_factory=cursor_factory)
        else:
            cur = get_db().cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
    except Exception as e:
        logger.error("[DB ERROR] {}\n L___ {}", str(e), query)
        rv = (None,)
    finally:
        cur.close()
    return (rv[0] if rv else None) if one else rv


def get_class1():
    return query_db("select distinct class1 from adminzone_meta order by class1")

def get_class2(class1):
    return query_db("select distinct class1, class2 from adminzone_meta where class1 = '{}' order by class1, class2".format(class1.encode("utf-8")))

def get_class3(class1, class2):
    return query_db("select distinct class1, class2, class3 from adminzone_meta where class1 = ? and class2 = ? order by class1, class2, class3", class1.encode("utf-8"), class2.encode("utf-8"))

def get_timing(class1, class2):
    return query_db("select distinct class1, class2, timing from adminzone_meta where class1 = '{}' and class2 = '{}' order by class1, class2, timing".format(class1.encode("utf-8"), class2.encode("utf-8")))

def get_all_meta():
    # 결과를 col_name:value 딕셔너리로 만든다.
    # http://initd.org/psycopg/docs/extras.html
    return query_db("select * from adminzone_meta order by class1, class2, class3", cursor_factory=psycopg2.extras.NamedTupleCursor)


### EVENT
@app.route('/test')
def hello():
    return "GeepsAdminZoneService Activated!"


@app.route('/api/get_class1')
def api_get_class1():
    out_list = list()
    for row in get_class1():
        out_list.append(row[0])

    ret = Response(json.dumps(out_list, ensure_ascii=False), mimetype='text/json')
    ret.content_encoding = 'utf-8'
    ret.headers.set("Cache-Control", "public, max-age=604800")

    return ret


@app.route('/service_page')
def service_page():
    class1_list = get_class1()
    class2_list = get_class2(unicode(class1_list[0][0]))
    timing_list = get_timing(class2_list[0][0], class2_list[0][1])
    all_meta = get_all_meta()

    return render_template("service_page.html",
                           class1_list=class1_list,
                           class2_list=class2_list,
                           timing_list=timing_list,
                           all_meta=all_meta)

if __name__ == '__main__':
    app.run()
