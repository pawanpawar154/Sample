import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate(r"C:\Users\003\OneDrive\Desktop\MediReport\firebase_key.json.json")
firebase_admin.initialize_app(cred)
