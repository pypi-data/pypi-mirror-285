import json

from google.cloud import storage
from flask import Response, request
from flask_restful import Resource
import pandas as pd
from database.cloud_storage import util as gcs_util
from pathlib import Path
from model.file_info import FileExtension
from io import BytesIO
import zipfile


class GetFileFromGCS(Resource):
    def post(self):
        try:
            data = request.get_json()
            bucket_name = data.get('bucket_name')
            path = data.get('path')
            file_type = data.get('file_type', None)
            extension = FileExtension(Path(path).suffix.upper())
            if file_type:
                extension = FileExtension(file_type.upper())
            if extension == FileExtension.csv:
                df = gcs_util.get_csv_from_gcs(bucket_name, path)
                return Response(df.to_csv(index=False), mimetype='text/csv',
                                headers={"Content-disposition": "attachment; filename=dataframe.csv"})
            elif extension == FileExtension.xlsx:
                df = gcs_util.get_csv_from_gcs(bucket_name, path)
                output = pd.ExcelWriter('dataframe.xlsx', engine='openpyxl')
                df.to_excel(output, index=False)
                output.save()
                output.seek(0)
                return Response(output.read(),
                                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                headers={"Content-disposition": "attachment; filename=dataframe.xlsx"})
            elif extension == FileExtension.json:
                json_data = json.loads(gcs_util.get_file_as_string_from_gcs(bucket_name, path))
                return json_data
            else:
                return {"error": "not match any extension"}, 500
        except Exception as e:
            return {"error": str(e)}, 500


class GetWholeFileFromGCSFolder(Resource):
    def post(self):
        try:
            data = request.get_json()
            bucket_name = data.get('bucket_name')
            path = data.get('path')
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            # 壓縮檔案夾中的所有檔案
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zf:
                for blob in bucket.list_blobs(prefix=path):
                    file_buffer = BytesIO()
                    blob.download_to_file(file_buffer)
                    file_buffer.seek(0)
                    zf.writestr(blob.name, file_buffer.getvalue())

            # 設定回傳的壓縮檔
            memory_file.seek(0)
            return Response(memory_file, mimetype='application/zip',
                            headers={"Content-disposition": f"attachment; filename=files.zip"})

        except Exception as e:
            return {"error": str(e)}, 500


class UploadFileToGCS(Resource):
    def post(self):
        try:
            bucket_name = request.form.get('bucket_name')
            path = request.form.get('path')
            if 'file' not in request.files:
                return {"error": "No file provided"}, 400

            file = request.files['file']
            if file.filename == '':
                return {"error": "No file selected"}, 400
            gcs_util.upload_file_to_gcs(bucket_name, path, file)
            return "", 200
        except Exception as e:
            return {"error": str(e)}, 500
