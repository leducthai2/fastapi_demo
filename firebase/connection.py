import os

import firebase_admin
from firebase_admin import credentials, firestore


current_dir = os.path.dirname(__file__)
cred_path = os.path.abspath(os.path.join(current_dir, f'../credentials/service_account_key.json'))
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()