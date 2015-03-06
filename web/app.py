from flask import Flask
from flask import request, render_template
import sunlight

app = Flask(__name__)
app.config.from_pyfile('app.settings')


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/bills/<bid>', methods=['GET'])
def bill(bid):
    sunlight.config.API_KEY = app.config.get('SUNLIGHT_API_KEY')
    bill = sunlight.congress.bills(bill_id=bid, 
        fields=app.config.get('SUNLIGHT_BILL_FIELDS'))
    return render_template('bill.html', bill=bill[0])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config.get('PORT'))

