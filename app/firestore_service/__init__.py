from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

from .upload_data import get_data, save_data

credential = credentials.ApplicationDefault()
firebase_admin.initialize_app(credential)

db = firestore.client()


def _get_timestamp(datestr=None):
    date = None
    date_format = '%d/%m/%Y'
    if not datestr:
        today = datetime.now().strftime(date_format)
        date = datetime.strptime(today, date_format)
    else:
        date = datetime.strptime(datestr, date_format)
    return date.timestamp()


def _is_db_updated():
    today_timestamp_id = _get_timestamp()
    doc_ref = db.collection('history').document(str(today_timestamp_id))
    doc = doc_ref.get()
    return doc.exists


def _get_last_update():
    collection = db.collection('history')
    query = collection.order_by(
        "timestamp", direction=firestore.Query.DESCENDING).limit(1)
    data = [case.to_dict() for case in query.get()]
    if (len(data)):
        return data[0]
    else:
        return None


def _save_new_data(data, db, count):
    save_data(data, db)

    date_format = '%d/%m/%Y'
    today_timestamp_id = _get_timestamp()
    date = datetime.now().strftime(date_format)

    collection = db.collection('history')
    ref = collection.document(str(today_timestamp_id))
    ref.set({
        'timestamp': today_timestamp_id,
        'date': date,
        'records': count
    })

    print('DB has been updated with the latest information')


def check_db_updates():
    if not _is_db_updated():
        data = get_data()
        new_records_count = len(data)

        print(new_records_count)

        last_update = _get_last_update()

        if last_update:
            last_count = last_update['records']

            if (new_records_count > last_count):
                _save_new_data(data[last_count:], db, new_records_count)
            else:
                print('No DB updates made. No new information.')
        else:
            _save_new_data(data, db, new_records_count)


def get_cases(data):
    collection = db.collection('cases')

    query = collection

    # TODO! Investigate what is indexes and why this is failing
    # if data.filter_by:
    #     for where_dict in data.filter_by:
    #         query = query.where(
    #             where_dict['field'], where_dict['operator'], where_dict['value'])

    query = query.order_by(
        data.order_by, direction=data.sort_by).limit(data.limit)

    snapshots = query.get()
    data = [case.to_dict() for case in snapshots]
    return data


class Query():
    order_by = 'timestamp',
    sort_by = firestore.Query.DESCENDING,
    limit = 100,
    filter_by = None,

    def __init__(self, order_by='timestamp',
                 sort_by='DESC',
                 limit=100,
                 filter_by=None):
        self.order_by = order_by
        self.sort_by = firestore.Query.DESCENDING if sort_by == 'DESC' else firestore.Query.ASCENDING
        self.limit = limit
        self.filter_by = filter_by
