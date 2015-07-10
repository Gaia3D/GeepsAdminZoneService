# -*- coding: utf-8 -*-
from flask import Flask, g
import psycopg2
import psycopg2.extras

app = Flask(__name__)

DATABASE = "dbname=postgis user=postgres"


def connect_to_database():
    return psycopg2.connect(DATABASE)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.colose()


def query_db(query, args=(), one=False):
    cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/test')
def hello():
    return "GeepsAdminZoneService Activated!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


@app.route('/api/get_class1')
def get_class1():
    out_str = None
    try:
        for row in query_db("select distinct class1 from adminzone_meta order by class1"):
            if not out_str:
                out_str = row['class1']
            else:
                out_str += "<br/>"+row['class1']

    except Exception as e:
        print e

    return out_str

if __name__ == '__main__':
    app.run()
