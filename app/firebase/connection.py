"""Firebase connection"""
import os
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS'))
firebase_admin.initialize_app(cred, {
    'storageBucket': 'nlp-ai-473a5.appspot.com'
})
