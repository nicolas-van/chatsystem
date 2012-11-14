
from gevent.wsgi import WSGIServer
import gevent
import gevent.monkey
import gevent.event
import flask

gevent.monkey.patch_all()

import pyphilo
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import select
from flask import Flask
app = Flask(__name__)
app.debug = True

posted = gevent.event.Event()

Session = sessionmaker(bind=pyphilo.engine)

@app.route("/")
def hello():
    return "Hello World 2!"

@app.route("/poll", methods=["POST"])
def poll():
    data = flask.request.json
    last = data["last"]
    while True:
        session = Session()
        try:
            query = session.query(Message)
            if last is not None:
                query = query.filter(Message.id > last)
            query = query.order_by(Message.id)
            res = query.all()
            lst = [x.message for x in res]
            if len(lst) > 0:
                plast = last
                last = res[-1].id
                if plast is not None:
                    return flask.jsonify({"res": lst, "last": last})
        finally:
            session.rollback()
        posted.wait()
        print "waking up"

@app.route("/post", methods=["POST"])
def post():
    data = flask.request.json
    session = Session()
    try:
        session.add(Message(message=data["message"]))
        session.execute("notify received_message;")
        session.commit()
    finally:
        session.rollback()
    return flask.jsonify({"res": None})

def listener():
    while True:
        session = Session()
        try:
            conn = session.connection().connection
            import psycopg2.extensions
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            c = conn.cursor()
            c.execute("listen received_message;")
            print "waiting"
            if select.select([conn], [], [], 5) == ([],[],[]):
                print "Timeout"
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop()
                    print "Got NOTIFY:", notify.pid, notify.channel, notify.payload
                    posted.set()
                    posted.clear()
        finally:
            session.rollback()

class Message(pyphilo.Base):
    message = sa.Column(sa.String(200))

if __name__ == "__main__":
    pyphilo.engine.init_global_engine("postgresql+psycopg2://niv@/messages")
    pyphilo.init_db()
    gevent.spawn(listener)
    httpd = WSGIServer(('', 5000), app).serve_forever()
