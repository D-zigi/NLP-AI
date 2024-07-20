"""Firebase Models for database collections"""
import os
from firebase_admin import firestore
from .buckets import Bucket

db = firestore.client()
bucket = Bucket()

TMP_PATH = os.environ['TMP_PATH']

class AppRoom:
    """app room model of '<app_name>-rooms' collection"""
    def __init__(self, ip, app_name):
        self.ip = ip
        self.app_name = app_name
        self.app_rooms = db.collection(f"{app_name}-rooms")
        self.data_url = f"{app_name}-rooms/{ip}.pkl"
        self.local_data_path = f"{TMP_PATH}/{app_name}-rooms/{ip}.pkl"

    def to_dict(self):
        """
        convert self object to dict
        """
        return {
            'data_url': self.data_url,
            'local_data_path': self.local_data_path
        }

    def exists(self):
        """
        check if self object exists in firebase
        """
        exists_flag = self.app_rooms.document(self.ip).get().exists
        return exists_flag

    def save(self):
        """
        upload self object to firebase
        """
        self.app_rooms.document(self.ip).set(self.to_dict())

    def delete(self):
        """
        delete self object from firebase
        """
        self.app_rooms.document(self.ip).delete()

    def download_data(self):
        """
        load self object from firebase storage
        """
        bucket.download_file(self.data_url, self.local_data_path)

    def upload_data(self):
        """
        upload self object to firebase storage
        """
        bucket.upload_file(self.local_data_path, self.data_url)
