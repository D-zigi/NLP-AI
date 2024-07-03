"""Firebase storage management"""
from firebase_admin import storage

class Bucket:
    """Firebase buket management"""
    def __init__(self):
        self.bucket = storage.bucket()
        self.name = self.bucket.name

    def upload_file(self, local_file_path, source_blob_name):
        """
        Upload a file to Firebase Storage
        from source_blob_name
        to local_file_path 
        """
        blob = self.bucket.blob(source_blob_name)
        blob.upload_from_filename(local_file_path)

        print(f'File {source_blob_name} uploaded to Firebase Storage.')

    def download_file(self, source_blob_name, local_file_path):
        """
        Download a file from Firebase Storage
        from local_file_path 
        to source_blob_name
        """
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(local_file_path)

        print(f'File {source_blob_name} downloaded from Firebase Storage.')
