from datetime import datetime

import requests

API_URL = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/json'


def get_data():
    res = requests.get(API_URL)
    res_dict = res.json()
    data = res_dict['records']
    return data


def _batch_save(data_arr, db):
    batch = db.batch()
    collection = db.collection('cases')

    for data in data_arr:
        day = data.get('day').zfill(2)
        month = data.get('month').zfill(2)
        year = data.get('year')
        date = datetime.strptime(data.get('dateRep'), '%d/%m/%Y')
        country_code = data.get('geoId')
        id = f"{day}{month}{year}-{country_code}"

        document = {
            'continent': data.get('continentExp'),
            'country': data.get('countriesAndTerritories'),
            'country_code': country_code,
            'cases': int(data.get('cases')),
            'deaths': int(data.get('deaths')),
            'date': data.get('dateRep'),
            'timestamp': date.timestamp(),
        }

        doc = collection.document(id)
        batch.set(doc, document)

    batch.commit()


def save_data(cases, db):
    max_len = 400

    if len(cases) > max_len:
        _batch_save(cases[:max_len], db)
        save_data(cases[max_len:], db)
    else:
        _batch_save(cases, db)
