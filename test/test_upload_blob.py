import unittest
from unittest.mock import patch, MagicMock
import os 
from app.utils.upload_blob import upload_to_blob
from azure.storage.blob import BlobServiceClient
import json 
import random
import string

@unittest.skipIf(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING") is None,
    "Required environment variables are not set",
)
class TestUploadToBlob(unittest.TestCase):

    def setUp(self):

        self.container_name = "test-container"
        self.name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        # Register the cleanup function
        self.addCleanup(self.cleanup_blob)

    def cleanup_blob(self):
        # Delete the blob
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.get_container_client(self.container_name)
        try:
            print(f"Cleaning up blob: {self.name}")
            container_client.delete_blob(self.name)
        except Exception as e:
            print(f"Failed to clean up blob: {self.name}, error: {e}")

    def test_upload_to_blob_success(self):
        # Test uploading to blob for real

        data = {'test': 'data'}
        upload_to_blob(json.dumps(data), "test-container", self.name)

        # Verify that the blob was uploaded successfully

        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(self.container_name)

        # Download the blob and verify its content
        downloaded_blob = container_client.download_blob(self.name).readall()
        self.assertEqual(json.loads(downloaded_blob.decode()), data)
        
if __name__ == "__main__":
    unittest.main()
