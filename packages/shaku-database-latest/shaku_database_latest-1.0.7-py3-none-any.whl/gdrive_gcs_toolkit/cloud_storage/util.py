import pandas as pd
from google.cloud import storage
from pathlib import Path


def get_csv_from_gcs(bucket_name, path):
    full_path = 'gs://{bucket}/{path}'.format(bucket=bucket_name, path=path)
    file_type = path.split(".")[-1]
    if file_type == 'csv':
        result_df = pd.read_csv(full_path)
    elif file_type in ('xlsx','xls'):
        with open(full_path, 'rb') as f: # For XLSX file, read in binary format to prevent decode errors
            result_df = pd.read_excel(f, engine='openpyxl', skiprows = [0]) # Ignore first row header from source data
    return result_df


def get_all_file_from_gcs_folder(bucket_name, path, file_type='csv'):
    # Get all file with specific type (XLS or CSV) and return combined dataframe
    file_dict = {}
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        for blob in bucket.list_blobs(prefix=str(path)):
            current_path = Path(blob.name)
            if str(current_path) != str(path):
                full_path = 'gs://{bucket}/{path}'.format(bucket=bucket_name, path=str(current_path))
                if file_type == 'csv':
                    file = pd.read_csv(full_path)
                elif file_type == 'excel':
                    with open(full_path, 'rb') as f: # For XLSX file, read in binary format to prevent decode errors
                        file = pd.read_excel(f, engine='openpyxl', skiprows = [0]) # Ignore first row header from source data
                file_dict[current_path] = file
    except Exception as e:
        raise e
    return file_dict
