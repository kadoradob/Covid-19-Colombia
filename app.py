import requests
from flask import render_template, request, url_for, jsonify
from app import create_app
from app.firestore_service import get_cases, check_db_updates, Query

app = create_app()


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


@app.route('/firestore')
def test_firestore():
    check_db_updates()
    params = request.args
    country_code = params.get('country_code')
    filter_by = None

    if country_code:
        filter_by = [{
            'field': 'country_code',
            'operator': '==',
            'value': params.get('country_code')
        }]

    query = Query(
        order_by=params.get('orderby'),
        sort_by=params.get('sortby'),
        limit=int(params.get('limit')),
        filter_by=filter_by
    )

    cases = get_cases(query)
    res = {
        'count': len(cases),
        'records': cases
    }
    return jsonify(res)


@app.route('/')
def home():
    data = {
        'title': APP_TITLE,
        'styles': get_asset_paths(BASE_STYLES)
    }
    return render_template('index.html', **data)


if __name__ == "__main__":
    app.run('localhost', 4200, debug=True)
