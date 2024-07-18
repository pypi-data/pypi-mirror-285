from typing import List, Dict

import pandas as pd
from google.cloud import storage
from pathlib import Path
from google.oauth2 import service_account

def get_csv_from_gcs(bucket_name, path):
    full_path = 'gs://{bucket}/{path}'.format(bucket=bucket_name, path=path)
    file_type = path.split(".")[-1]
    result_df = pd.DataFrame()
    if file_type == 'csv':
        result_df = pd.read_csv(full_path)
    elif file_type == 'xlsx' or file_type == 'xls':
        result_df = pd.read_excel(full_path, engine='openpyxl')
    return result_df


def get_all_file_from_gcs_folder(bucket_name, path, file_type='csv'):
    # Download all CSV and Excel file under specific bucket folder as dataframe object
    file_dict = {}
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        for blob in bucket.list_blobs(prefix=str(path)):
            current_path = Path(blob.name)
            if str(current_path).endswith('sample.txt'): # ignore sample file
                print("Ignore sample file sample.txt")
                continue

            if str(current_path) != str(path):
                full_path = 'gs://{bucket}/{path}'.format(bucket=bucket_name, path=str(current_path))
                file = pd.DataFrame()
                file_type = full_path.split('.')[-1]
                if file_type == 'csv':
                    file = pd.read_csv(full_path)
                elif file_type in ('xls', 'xlsx', 'xlsm'):
                    # Specify sheet name when parsing XLS file for multiple sheets
                    # Specify different parsing rules that applies on all merchant, respective to different data sources
                    if 'ichef' in path: # for POS ichef
                        file = pd.read_excel(full_path)
                    if 'maifood' in path:  # for POS maifood
                        if 'dataoverview-prod' in path:
                            file = pd.read_excel(full_path, sheet_name='結帳單明細')
                        elif 'dataoverview-order' in path:
                            file = pd.read_excel(full_path, sheet_name='結帳單列表')
                    elif 'jkopay' in path:  # for DSP JKO-pay
                        print(f"jko file path: {full_path}")
                        file = pd.read_excel(full_path, sheet_name='支付請款明細')
                    else:
                        file = pd.read_excel(full_path)

                else:
                    raise ValueError("File not valid type! Invalid file in path: {}".format(full_path))
                file_dict[current_path] = file
    except Exception as e:
        raise ValueError(e)
    return file_dict


def get_file_as_string_from_gcs(bucket_name, path) -> bytes:
    # Load file content from file in bucket folder as string
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(path)

    # Download the contents of the blob as a string and then parse it using json.loads() method
    return blob.download_as_string(client=None)


def get_all_json_from_gcs(bucket_name, folder_path) -> Dict[str, bytes]:
    # Get all JSON object information from bucket folder path
    # Output: bucker file name, json content
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_path)
    result_dict = {}
    for blob in blobs:
        if blob.name.endswith('.json'):
            result_dict[blob.name] = blob.download_as_string(client=None)
    return result_dict


def upload_json_to_gcs(bucket_name, destination_blob_name, json_data):
    # 初始化GCS客户端
    client = storage.Client()

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(json_data, content_type='application/json')


def delete_file_from_gcs(bucket_name, file_name):
    # 初始化 GCS 客户端
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.delete()
    print(f'Successfully deleted file  {file_name} from {bucket_name}.')


def upload_file_to_gcs(target_bucket_name, folder_path, file):
    # Upload local object to GCS bucket
    bucket_folder_path = 'gs://' + str(target_bucket_name) + '/' +  str(folder_path) # Format GCS target folder URL to upload
    folder_file_suffix = '.' + str(bucket_folder_path).split('.')[-1] # Get suffix: .xlsx, .xls, or other type
    bucket_folder_path_csv = str(bucket_folder_path).replace(folder_file_suffix, '.csv')
    print(f"Bucket folder csv path: {bucket_folder_path_csv}")
    file.to_csv(bucket_folder_path_csv, index = False) # save dataframe object to GCS bucket folder
    return {"public_url": bucket_folder_path}

def move_blob(source_bucket: str, source_blob_file: str, destination_bucket: str, destination_blob_file: str):
    """Moves a blob from one bucket to another with a new name."""
    # source_bucket : "your-bucket-name"
    # source_blob_file: Str = "/path/to/file/under/source_bucket.txt"
    # destination_bucket = "destination-bucket-name"
    # destination_blob_file = "/path/to/file/under/destination_bucket.txt"
    storage_client = storage.Client()

    source_bucket = storage_client.bucket(source_bucket)
    source_blob = source_bucket.get_blob(source_blob_file)
    
    destination_bucket = storage_client.bucket(destination_bucket)
    
        # Optional: set a generation-match precondition to avoid potential race conditions
        # and data corruptions. The request is aborted if the object's
        # generation number does not match your precondition. For a destination
        # object that does not yet exist, set the if_generation_match precondition to 0.
        # If the destination object already exists in your bucket, set instead a
        # generation-match precondition using its generation number.
        # There is also an `if_source_generation_match` parameter, which is not used in this example.
    # if target file already exists in bucket folder, set this to None. 
    # if target file not exist yet, set it to 0
    if source_blob.exists(): # if file already exist in bucket folder
        destination_generation_match_precondition = None # set to None only when target destination exist already
    else:
        destination_generation_match_precondition = 0  

    blob_copy = source_bucket.copy_blob(
            source_blob, destination_bucket, destination_blob_file, if_generation_match=destination_generation_match_precondition,
    )