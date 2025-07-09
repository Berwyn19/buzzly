import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, initialize_app, storage, firestore

# Load .env variables
load_dotenv()

# Only initialize if not already done (to prevent FastAPI reload issues)
if not firebase_admin._apps:
    firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    firebase_credentials["private_key"] = firebase_credentials["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(firebase_credentials)
    initialize_app(cred, {
        'storageBucket': 'ugcgenerator-5884a.firebasestorage.app'  # Your actual bucket
    })

