import flask

app = flask.Flask(__name__)

@app.route('/test')
def form():
  return 'hello'
