import requests
from flask import Flask, render_template, request, url_for, jsonify

app = Flask(__name__)


def get_asset_paths(paths):
    return [url_for('static', filename=path) for path in paths]


APP_TITLE = 'COVID-19 Open Data'
BASE_STYLES = [
    'css/reset.css',
    'css/main.css'
]


@app.errorhandler(404)
def page_not_found(error):
    styles = BASE_STYLES.copy()
    styles.append('css/error-page.css')
    data = {
        'title': 'Error 404 - ' + APP_TITLE,
        'styles': get_asset_paths(styles),
        'error_code': 404,
        'error_msg': 'Oops! The page you are looking for is not available or doesn\'t exist.'
    }
    return render_template('error-handler.html', **data), 404


@app.errorhandler(500)
def special_exception_handler(err):
    styles = BASE_STYLES.copy()
    styles.append('css/error-page.css')
    data = {
        'title': 'Error 500 - ' + APP_TITLE,
        'styles': get_asset_paths(styles),
        'error_code': 500,
        'error_msg': 'Oops! There was an issue processing your request, please try again later.'
    }
    return render_template('error-handler.html', **data), 500


@app.route('/data')
def get_data():
    res = requests.get(
        'https://opendata.ecdc.europa.eu/covid19/casedistribution/json')
    dict_res = res.json()
    return jsonify(dict_res)


@app.route('/')
def home():
    data = {
        'title': APP_TITLE,
        'styles': get_asset_paths(BASE_STYLES)
    }
    return render_template('index.html', **data)


if __name__ == "__main__":
    app.run(debug=True)
