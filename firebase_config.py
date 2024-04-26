# firebase_config.py

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

def initialize_firebase():
    cred = credentials.Certificate("serviceAccountKey.json")
    
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred, {
            'databaseURL': '',
            'storageBucket': ''
        })

    ref = db.reference('Students')
    encodings_ref = db.reference('Encodings')
    bucket = storage.bucket()
    
    return bucket, ref, encodings_ref
