import time
from typing import List, Dict

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from datetime import datetime

def get_table_info(dataset, table_name, credentials=None):
    client = bigquery.Client(credentials=credentials)
    # table_id = 'your-project.your_dataset.your_table'
    full_table_id = f'{dataset}.{table_name}'
    table = client.get_table(full_table_id)
    return table.schema

def is_valid_datetime(date_value):
# Validate if datetime value is in format %Y-%m-%d, if not then return False
  try:
    date_value = datetime.strptime(date_value, "%Y-%m-%d")  # Example format, adjust as needed
    return True
  except Exception:
    return False

def validate_dataframe_type_with_bq(df, target_dataset, target_table, credentials=None):
    try:
        table_schema = get_table_info(target_dataset, target_table, credentials=credentials)
        for col_info in table_schema:
            if col_info.name in df.columns:
                if col_info.field_type == 'STRING':
                    df[col_info.name] = df[col_info.name].astype(str)
                    df.loc[df[col_info.name] == 'None', col_info.name] = None
                elif col_info.field_type == 'FLOAT':
                    df[col_info.name] = df[col_info.name].astype(float)
                elif col_info.field_type == 'INTEGER':
                    df[col_info.name] = df[col_info.name].astype('Int64')
                elif col_info.field_type == 'TIMESTAMP':
                    df[col_info.name] = pd.to_datetime(df[col_info.name])
                elif col_info.field_type == 'DATETIME':
                    df[col_info.name] = pd.to_datetime(df[col_info.name]).dt.tz_localize(None)
                else:
                    df[col_info.name] = df[col_info.name].astype(object)
                    df.loc[df[col_info.name] == 'None', col_info.name] = None
    except Exception as e:
        print("[ERROR] --> Convert column type error,or Key Error")
        raise e
    return df


def save_data_to_bq(insert_df, dataset_id, table_id, credentials=None, schema = None):
    try:
        client = bigquery.Client(credentials=credentials)
        # 資料表參數
        print("Dataset_id: {}  table_id: {}".format(dataset_id, table_id))
        table_ref = client.dataset(dataset_id).table(table_id)
        print("Create table ref done.")
        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = False # Avoid auto-detection, to make sure use provided schema to match
        #job_config.source_format = bigquery.SourceFormat.CSV
        if schema: # If schema provided, may be creating _tmp table for merging
            job_config.schema = schema
            print("received provided schema!")
        else: # if schema not provided, then use table name to get the schema
            table_schema = get_table_info(dataset_id, table_id, credentials=credentials)
            job_config.schema = table_schema # manually define table_schema from BQ table
        
        print("Received schema from bigquery: {}".format(job_config.schema))
        job = client.load_table_from_dataframe(insert_df, table_ref, job_config=job_config)  # Very large scale dataframe, but cannot ignore missing columns
        job.result()
        print("Done insertion.")

    except Exception as e:
        raise e


def query_multiple_data_from_bq(sql_list, data_name, credentials=None):
    try:
        client = bigquery.Client(credentials=credentials)
        result_dict = {}
        for sql, alias in zip(sql_list, data_name):
            results = client.query(sql)
            df = results.to_dataframe()
            result_dict[alias] = df
    except Exception as e:
        raise e
    return result_dict


def check_table_exist(table_id, credentials=None):
    client = bigquery.Client(credentials=credentials)

    try:
        client.get_table(table_id)  # Make an API request.
        print("Table {} already exists.".format(table_id))
        return True
    except NotFound:
        print("Table {} is not found.".format(table_id))
        return False


def create_table(table_name, column_info_dict: Dict[str, Dict[str, str]]):
    client = bigquery.Client()
    schema = [bigquery.SchemaField(col, val['type'], mode=val.get("mode", None))
              for col, val in column_info_dict.items()]
    table = bigquery.Table(table_name, schema=schema)
    table = client.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )


def create_partition_table(project_id, dataset, table_name, column_info_dict: Dict[str, Dict[str, str]],
                           partition_column: str,
                           partition_date_trunc: str, integer_partition_start: int = None,
                           integer_partition_end: int = None, integer_partition_interval: int = None,
                           cluster_columns: List[str] = None):
    try:
        client = bigquery.Client()
        schema = [bigquery.SchemaField(col, val['type'], mode=val.get("mode", None))
                  for col, val in column_info_dict.items()]
        full_table_name = f"{project_id}.{dataset}.{table_name}"
        table = bigquery.Table(full_table_name, schema=schema)
        if cluster_columns:
            table.clustering_fields = cluster_columns
        integer_partition = False
        if partition_date_trunc.upper() == 'DAY':
            date_trunc_type = bigquery.TimePartitioningType.DAY
        elif partition_date_trunc.upper() == 'MONTH':
            date_trunc_type = bigquery.TimePartitioningType.MONTH
        elif partition_date_trunc.upper() == 'HOUR':
            date_trunc_type = bigquery.TimePartitioningType.HOUR
        elif partition_date_trunc.upper() == 'YEAR':
            date_trunc_type = bigquery.TimePartitioningType.YEAR
        elif partition_date_trunc.upper() == 'INTEGER':
            integer_partition = True
        else:
            raise "not match any partition date_trunc"
        if integer_partition:
            table.range_partitioning = bigquery.RangePartitioning(
                # To use integer range partitioning, select a top-level REQUIRED /
                # NULLABLE column with INTEGER / INT64 data type.
                field=partition_column,
                range_=bigquery.PartitionRange(start=integer_partition_start, end=integer_partition_end,
                                               interval=integer_partition_interval),
            )
        else:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=date_trunc_type,
                field=partition_column,  # name of column to use for partitioning
            )
        table = client.create_table(table)  # Make an API request.

        print(
            "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
        )
    except Exception as e:
        raise e


def merge_table(project_name: str, target_table: str, target_dataset, source_df: pd.DataFrame, unique_keys: List[str],
                update_cols: List[str] = None, exclude_update_col: List[str] = None, credentials=None):
    # Merging: use source_df to add into target table
    # if sale_id, shop_id already exist, then update value. Else insert new row from source_df into target table
    try:
        print("Start Merge Table")
        client = bigquery.Client(credentials=credentials)
        merge_sql = """MERGE {project_name}.{target_dataset}.{target_table} T
                        USING {project_name}.{target_dataset}.{target_table}_tmp S
                        ON {merge_condition}
                        WHEN MATCHED THEN
                        update set {match_sql}
                        WHEN NOT MATCHED THEN
                        INSERT ({T_columns}) values ({S_columns})"""
        merge_condition = " and ".join([f"T.{col} = S.{col}" for col in unique_keys])
        if update_cols:
            match_sql = ",".join([f"T.{col} = S.{col}" for col in update_cols])
        elif exclude_update_col:
            match_sql = ",".join([f"T.{col} = S.{col}" for col in source_df.columns
                                  if col not in exclude_update_col or col not in unique_keys])
        else:
            match_sql = ",".join([f"T.{col} = S.{col}" for col in source_df.columns if col.lower() not in unique_keys])

       
        S_columns = ",".join([f"S.{col}" for col in source_df.columns])
        T_columns = S_columns.replace('S.', '')


        merge_sql = merge_sql.format(target_dataset=target_dataset, target_table=target_table,
                                     merge_condition=merge_condition, match_sql=match_sql, project_name=project_name,
                                     T_columns = T_columns, S_columns = S_columns)
        print(f"Merge SQL : {merge_sql}")
        validated_df = validate_dataframe_type_with_bq(source_df, target_dataset, target_table)
        target_schema = get_table_info(target_dataset, target_table)
        print(f"Target dataset {target_dataset} target table: {target_table} target schema: {target_schema}")
        
        print("Start create tmp table")
        target_tmp_table = target_table + "_tmp"

        save_data_to_bq(validated_df, target_dataset, target_tmp_table, schema = target_schema) # tmp
        print("create tmp table End")
        print("Start merge")
        start = time.time()
        query_job = client.query(merge_sql)
        query_job.result()
        total_time = str(time.time() - start)
        print(f"End merge : {total_time} seconds")
        client.delete_table(f"{target_dataset}.{target_table}_tmp", not_found_ok=True)
    except Exception as e:
        print(e)
        print("[ERROR]--> Merge Table Error")
