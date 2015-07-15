# -*- coding: utf-8 -*-
from flask import Flask, g, json, render_template, Response, request
import psycopg2
import psycopg2.extras
from Config import Config
import logging
import os.path
from subprocess import call
import tempfile
from zipfile import *

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
    return query_db("select distinct class2 from adminzone_meta where class1 = '{}' order by class2".format(class1.encode("utf-8")))

def get_class3(class1, class2):
    return query_db("select distinct class1, class2, class3 from adminzone_meta where class1 = ? and class2 = ? order by class1, class2, class3", class1.encode("utf-8"), class2.encode("utf-8"))

def get_timing(class1, class2):
    return query_db("select distinct timing, table_name from adminzone_meta where class1 = '{}' and class2 = '{}' order by timing desc".format(class1.encode("utf-8"), class2.encode("utf-8")))

def get_all_meta():
    # 결과를 col_name:value 딕셔너리로 만든다.
    # http://initd.org/psycopg/docs/extras.html
    return query_db("select * from adminzone_meta order by class1, class2, class3, timing desc", cursor_factory=psycopg2.extras.NamedTupleCursor)

def get_all_meta_json():
    res = get_all_meta()

    dict_res = dict()
    for row in res:
        class1 = row.class1
        level = 1
        class2 = row.class2
        if class2: level = 2
        class3 = row.class3
        if class3: level = 3
        data = {'table_name':row.table_name, 'timing':row.timing, 'agency':row.agency,
                'source_url':row.source_url, 'image_url':row.image_url, 'source_name':row.source_name,
                'description':row.description}

        if level == 1:
            if not dict_res.has_key(class1):
                dict_res[class1] = list()
            dict_res[class1].append(data)
        elif level == 2:
            if not dict_res.has_key(class1):
                dict_res[class1] = dict()
            if not dict_res[class1].has_key(class2):
                dict_res[class1][class2] = list()
            dict_res[class1][class2].append(data)
        else: # level == 3
            if not dict_res.has_key(class1):
                dict_res[class1] = dict()
            if not dict_res[class1].has_key(class2):
                dict_res[class1][class2] = dict()
            if not dict_res[class1][class2].has_key(class3):
                dict_res[class1][class2][class3] = list()
            dict_res[class1][class2][class3].append(data)

    return json.dumps(dict_res, ensure_ascii=False)

def get_count_info():
    return query_db("select (select count(*) as n_class1 from (select distinct class1 from adminzone_meta) as t_class1), (select count(*) as n_total from adminzone_meta)")

### EVENT
@app.route('/test')
@app.route('/adminzone/test')
def hello():
    return "GeepsAdminZoneService Activated!"


@app.route('/api/get_class1')
@app.route('/adminzone/api/get_class1')
def api_get_class1():
    out_list = list()
    for row in get_class1():
        out_list.append(row[0])

    ret = Response(json.dumps(out_list, ensure_ascii=False), mimetype='text/json')
    ret.content_encoding = 'utf-8'
    ret.headers.set("Cache-Control", "public, max-age=604800")

    return ret


@app.route('/api/get_all_meta')
@app.route('/adminzone/api/get_all_meta')
def api_get_all_meta():
    json_res = get_all_meta_json()
    ret = Response(json_res, mimetype='text/json')
    ret.content_encoding = 'utf-8'
    ret.headers.set("Cache-Control", "public, max-age=604800")

    return ret


@app.route('/service_page')
@app.route('/adminzone/service_page')
def service_page():
    count_info = get_count_info()
    all_meta_json = get_all_meta_json()

    return render_template("service_page.html",
                           count_info=count_info[0],
                           metadata=all_meta_json,
                           crs_list=config.crs_list)

@app.route('/makefile')
@app.route('/adminzone/makefile')
def makefile():
    table_name = request.args.get('table_name', None)
    crs = request.args.get('crs', None)

    if not crs:
        return Response("crs 인자가 필요합니다.", 400)
    if not table_name:
        return Response("table_name 인자가 필요합니다.", 400)

    # crs 있는지 확인
    # if not ("EPSG:"+crs) in config.crs_list:
    res = query_db("select count(*) from spatial_ref_sys where srid = %s", args=(crs,), one=True)
    if res[0] <= 0:
        return Response("요청한 CRS가 없습니다.", 500)

    # table_name 있는지 확인
    res = query_db("select count(*) from adminzone_meta where table_name = %s", args=(table_name,), one=True)
    if res[0] <= 0:
        return Response("요청한 TABLE이 없습니다.", 500)

    # file name을 <table_name>__<crs>로 정함
    file_base = table_name+"__"+crs

    zip_file = os.path.join(config.download_folder, file_base+".zip")
    if os.path.isfile(zip_file):
        return Response("기존 파일 있음", 200)

    temp_dir = tempfile.gettempdir()
    shp_file = os.path.join(temp_dir, file_base+".shp")

    # 조회용 Query 만들기
    # http://splee75.tistory.com/93
    res = query_db(
        """
select string_agg(txt, ', ')
from (
SELECT concat('SELECT ', string_agg(column_name, ', ')) as txt
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name   = '{table_name}'
  AND udt_name != 'geometry'
union
SELECT concat('ST_Transform(', string_agg(column_name, ', '), ',{crs}) as geom FROM ""{table_name}""') as txt
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name   = '{table_name}'
  AND udt_name = 'geometry'
) tbl
        """.format(crs=crs, table_name=table_name),
    one=True)
    sql = res[0]

    try:
        # Shape 파일 만들기
        command = 'pgsql2shp -f {shp_file} -u {user} -P {pwd} {database} "{sql}"'.format(
            shp_file=shp_file, user=config.db_user, pwd=config.db_pwd, database=config.db_database, sql=sql)
        logger.debug(command)
        rc = call(command)
        if rc != 0:
            return Response("Shape 파일 생성 중 오류", 500)

        with ZipFile(zip_file, 'w') as shape_zip:
            shape_zip.write(os.path.join(temp_dir, file_base+".shp"), arcname=file_base+".shp")
            shape_zip.write(os.path.join(temp_dir, file_base+".shx"), arcname=file_base+".shx")
            shape_zip.write(os.path.join(temp_dir, file_base+".dbf"), arcname=file_base+".dbf")
            shape_zip.write(os.path.join(temp_dir, file_base+".prj"), arcname=file_base+".prj")

        os.remove(os.path.join(temp_dir, file_base+".shp"))
        os.remove(os.path.join(temp_dir, file_base+".shx"))
        os.remove(os.path.join(temp_dir, file_base+".dbf"))
        os.remove(os.path.join(temp_dir, file_base+".prj"))
    except Exception as e:
        logger.error("Shape 파일 생성 중 오류: "+str(e))
        return Response("Shape 파일 생성 중 오류", 500)

    return Response("파일 생성 완료", 200)


@app.route('/download')
@app.route('/adminzone/download')
def download():
    table_name = request.args.get('table_name', None)
    crs = request.args.get('crs', None)

    if not crs:
        return Response("crs 인자가 필요합니다.", 400)
    if not table_name:
        return Response("table_name 인자가 필요합니다.", 400)

    # file name을 <table_name>__<crs>로 정함
    file_base = table_name+"__"+crs

    zip_file = os.path.join(config.download_folder, file_base+".zip")
    if not os.path.isfile(zip_file):
        return Response("ZIP 파일 없음", 500)

    try:
        with open(zip_file, "rb") as f:
            zip_bin = f.read()
    except Exception as e:
        logger.error("Shape 다운로드 중 오류: "+str(e))
        return Response("Shape 다운로드 중 오류", 500)

    ret = Response(zip_bin, mimetype='application/zip')
    ret.headers["Content-Disposition"] = "attachment; filename={}".format(file_base+".zip")
    return ret


if __name__ == '__main__':
    app.run()
