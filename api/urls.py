from api import app

@app.route('/')
@app.route('/index')
def index():
    return "Main Page"

@app.route('/api/v1.0/ping')
def ping():

    return "{answer: 'OK'}"