import firebase_admin
from firebase_admin import credentials, storage
import os


# Initialize Firebase Admin SDK
def init_firebase():
    cred = credentials.Certificate("firebase_service_account.json")
    firebase_admin.initialize_app(cred, {"storageBucket": "daivietgpt.appspot.com"})


def upload_file_to_firebase(file_path: str, file_name: str):
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_path)
    blob.make_public()
    return blob.public_url
