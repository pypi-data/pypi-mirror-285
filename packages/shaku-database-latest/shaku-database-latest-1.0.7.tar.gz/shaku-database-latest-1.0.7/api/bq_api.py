from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import pandas as pd
from database.bigquery import util as bq_until
from database.bigquery import bq_sql_parser
from database.bigquery.bq_sql_parser import TableInfo


class TableInfoResource(Resource):
    def get(self, dataset, table_name):
        try:
            schema = bq_until.get_table_info(dataset, table_name)
            return jsonify({"schema": str(schema)})
        except Exception as e:
            return {"error": str(e)}, 500


class CreateTableResource(Resource):
    def post(self):
        data = request.get_json()
        table_name = data.get('table_name')
        column_info_dict = data.get('column_info_dict')
        try:
            bq_until.create_table(table_name, column_info_dict=column_info_dict)
            return {"message": f"Table {table_name} created."}
        except Exception as e:
            return {"error": str(e)}, 500


class CreatePartitionTableResource(Resource):
    def post(self):
        data = request.get_json()
        table_name = data.get('table_name')
        project_id = data.get('project_id')
        dataset = data.get('dataset')
        column_info_dict = data.get('column_info_dict')
        partition_date_trunc = data.get('partition_date_trunc')
        partition_column = data.get('partition_column')
        integer_partition_start = data.get('integer_partition_start', None)
        integer_partition_end = data.get('integer_partition_end', None)
        integer_partition_interval = data.get('integer_partition_interval', None)
        cluster_columns = data.get('cluster_columns', None)
        try:
            bq_until.create_partition_table(project_id, dataset, table_name, column_info_dict, partition_column,
                                            partition_date_trunc, integer_partition_start, integer_partition_end,
                                            integer_partition_interval, cluster_columns)
            return {"message": f"Table {table_name} created."}
        except Exception as e:
            return {"error": str(e)}, 500


class InsertDataResource(Resource):
    def post(self):
        # 檢查是否有檔案上傳
        dataset_id = request.form.get('dataset_id')
        table_id = request.form.get('table_id')
        if 'file' not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files['file']
        if file.filename == '':
            return {"error": "No file selected"}, 400

        # 根據檔案類型讀取資料
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file, engine='openpyxl')
        else:
            return {"error": "Invalid file type"}, 400
        try:
            validated_df = bq_until.validate_dataframe_type_with_bq(df, dataset_id, table_id)
            bq_until.save_data_to_bq(validated_df, dataset_id, table_id)
        except Exception as e:
            return {"error": e}, 400

        return {"message": "Data uploaded successfully"}, 200


class MergeDataResource(Resource):
    def post(self):
        # 檢查是否有檔案上傳
        project_id = request.form.get('project_id')
        target_table = request.form.get('target_table')
        target_dataset = request.form.get('target_dataset')
        unique_keys = request.form.get('unique_keys')
        unique_keys = unique_keys.split(",")
        update_cols = request.form.get('update_cols', None)
        exclude_update_col = request.form.get('exclude_update_col', None)
        if 'file' not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files['file']
        if file.filename == '':
            return {"error": "No file selected"}, 400

        # 根據檔案類型讀取資料
        if file.filename.endswith('.csv'):
            source_df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            source_df = pd.read_excel(file, engine='openpyxl')
        else:
            return {"error": "Invalid file type"}, 400
        try:
            if (update_cols and not exclude_update_col) or (update_cols and exclude_update_col):
                bq_until.merge_table(project_id, target_table, target_dataset, source_df, unique_keys,
                                     update_cols)
            else:
                bq_until.merge_table(project_id, target_table, target_dataset, source_df, unique_keys,
                                     exclude_update_col)
        except Exception as e:
            return {"error": e}, 400

        return {"message": "Data uploaded successfully"}, 200


class BQSQLGeneratorResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            table_info_dict = data.get('table_info_dict', None)
            sql = data.get('sql')
            selected_columns = data.get('selected_columns', None)
            partition_col = data.get('partition_col', None)
            partition_start = data.get('partition_start', None)
            partition_end = data.get('partition_end', None)
            if table_info_dict or table_info_dict != {}:
                table_info_map = {table_name: TableInfo(table_info['unique_keys'], table_info['date_time_col'],
                                                        table_info['cast_col_map'])
                                  for table_name, table_info in table_info_dict.items()}
            else:
                raise "table_info_dict is None or empty dict"
            format_sql = bq_sql_parser.generate_sql_for_bq(sql, table_info_map, selected_columns, partition_col,
                                                           partition_start, partition_end)
            return format_sql
        except Exception as e:
            return {"error": str(e)}, 500
