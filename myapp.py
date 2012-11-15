
from gevent.wsgi import WSGIServer
import gevent
import gevent.monkey
import gevent.event
import flask

gevent.monkey.patch_all()
import gevent_psycopg2; gevent_psycopg2.monkey_patch()

import pyphilo
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import select
import time
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
                    print "found", len(lst), "messages"
                    return flask.jsonify({"res": lst, "last": last})
            else:
                print "didn't found any message"
        finally:
            session.close()
        posted.wait()
        print "waking up"

@app.route("/post", methods=["POST"])
def post():
    data = flask.request.json
    session = Session()
    try:
        session.add(Message(message=data["message"]))
        session.commit()
        session.execute("notify received_message, '"+ data["message"] + "'")
        session.commit()
    finally:
        session.rollback()
    return flask.jsonify({"res": None})

def listener():
    while True:
        conn1 = pyphilo.engine.connect()
        conn = conn1.connection
        try:
            import psycopg2.extensions
            c = conn.cursor()
            c.execute("listen received_message;")
            conn.commit();
            print "waiting"
            if select.select([conn], [], [], 10) == ([],[],[]):
                print "Timeout"
                c.execute("unlisten received_message;")
                conn.commit()
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop()
                    print "Got NOTIFY:", notify.pid, notify.channel, notify.payload
                    c.execute("unlisten received_message;")
                    conn.commit()
                    posted.set()
                    posted.clear()
        finally:
            conn1.close()

class Message(pyphilo.Base):
    message = sa.Column(sa.String(200))

if __name__ == "__main__":
    pyphilo.engine.init_global_engine("postgresql+psycopg2://niv@/messages")
    pyphilo.init_db()
    gevent.spawn(listener)
    httpd = WSGIServer(('', 5000), app).serve_forever()
