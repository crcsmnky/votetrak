from flask import Flask
from flask import request, render_template
from flask.ext.pymongo import PyMongo
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = '04559db538956949beaf26abe83162ec'

app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = 27017
app.config['MONGO_DBNAME'] = 'votetrak'

mongo = PyMongo(app)

toolbar = DebugToolbarExtension(app)

@app.route('/', methods=['GET'])
def index():
    bills = mongo.db.bills.find()
    updates = mongo.db.updates.find()
    return render_template('home.html', bills=bills, updates=updates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
