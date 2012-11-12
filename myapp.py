
from gevent.wsgi import WSGIServer
import gevent
import gevent.monkey
import gevent.event
import flask
import pyphilo
import sqlalchemy as sa
import select
from flask import Flask
app = Flask(__name__)
app.debug = True

posted = gevent.event.Event()
message = ""

@app.route("/")
def hello():
    return "Hello World 2!"

@app.route("/poll", methods=["POST"])
def poll():
    data = flask.request.json
    posted.wait()
    print "message", message
    return flask.jsonify({"res": message})

@app.route("/post", methods=["POST"])
def post():
    data = flask.request.json
    global message
    message = data['message']
    posted.set()
    posted.clear()
    return flask.jsonify({"res": None})

def listener():
    with pyphilo.session.begin():
        while True:
            print "waiting"
            pyphilo.session.execute("listen received_message")
            conn = pyphilo.session.connection().connection
            if select.select([conn], [], [], 60) == ([],[],[]):
                print "Timeout"
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop()
                    print "Got NOTIFY:", notify.pid, notify.channel, notify.payload

class Message(pyphilo.Base):
    message = sa.Column(sa.String(200))

if __name__ == "__main__":
    gevent.monkey.patch_all()
    pyphilo.engine.init_global_engine("postgresql+psycopg2://niv@/messages")
    pyphilo.init_db()
    gevent.spawn(listener)
    httpd = WSGIServer(('', 5000), app).serve_forever()
