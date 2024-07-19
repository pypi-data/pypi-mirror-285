import subprocess
from google.cloud import storage


# import gzip
# from sh import pg_dump


# with gzip.open(‘backup.gz’, ‘wb’) as f:
#   pg_dump(‘-h’, ‘localhost’, ‘-U’, ‘postgres’, ‘my_dabatase’, _out=f)

def dump_db():
    try:
        subprocess.run(['pg_dump', '--dbname=postgresql://user:password@localhost/dbname', '--file=dump_file_path'])
        print("Database dumped successfully.")
    except Exception as e:
        print("An error occurred while dumping the database.")
        print(str(e))


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client.from_service_account_json('path_to_service_account_file')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client.from_service_account_json('path_to_service_account_file')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print("Blob {} downloaded to {}.".format(source_blob_name, destination_file_name))


def restore_db():
    try:
        subprocess.run(
            ['pg_restore', '--dbname=postgresql://user:password@localhost/dbname', '--verbose', '--clean', '--no-acl',
             '--no-owner', '-U', 'myuser', '-d', 'mydb', 'dump_file_path'])
        print("Database restored successfully.")
    except Exception as e:
        print("An error occurred while restoring the database.")
        print(str(e))


# Call the functions
dump_db()
upload_blob('bucket_name', 'dump_file_path', 'object_name')
download_blob('bucket_name', 'object_name', 'dump_file_path')
restore_db()
