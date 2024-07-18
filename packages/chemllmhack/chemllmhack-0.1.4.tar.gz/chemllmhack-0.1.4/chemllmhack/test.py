import os

from google.cloud import storage

credential_path = "/Users/bowenzhang/.config/gcloud/application_default_credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

def list_buckets():
    """Lists all buckets."""

    storage_client = storage.Client(project="qdx-chem-llm-hackthon")
    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)



from google.cloud import storage


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client(project="qdx-chem-llm-hackthon")

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )




if __name__ == "__main__":
    # list_buckets()
    download_blob("hackthon_paper", "paper_db_test.chroma", "test.txt")