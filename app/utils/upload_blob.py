from azure.storage.blob import BlobServiceClient
import os

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "your-container-name"

blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)


def upload_to_blob(serialized_data, container_name, blob_name):
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)


    # Get a reference to the blob
    blob_client = container_client.get_blob_client(blob_name)

    # Upload the serialized data, overwriting if the blob already exists
    blob_client.upload_blob(serialized_data, overwrite=True)
