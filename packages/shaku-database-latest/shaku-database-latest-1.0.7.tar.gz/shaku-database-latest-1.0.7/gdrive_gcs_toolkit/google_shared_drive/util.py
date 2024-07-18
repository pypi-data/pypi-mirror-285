from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import pandas as pd
import io
from pathlib import Path
from zipfile import ZipFile
import requests

class GDriveToolkit:
    def __init__(self, shared_drive_id, key_file_path, path=None):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.KEY_FILE_PATH = key_file_path
        self.creds = service_account.Credentials.from_service_account_file(self.KEY_FILE_PATH, scopes=self.SCOPES)
        self.service = build('drive', 'v3', credentials=self.creds)
        self.shared_drive_id = shared_drive_id
        self.path = path
        if self.path:
            path_parts = Path(self.path)
            self.root_list = [path for path in path_parts.parts]
            if len(self.root_list) > 1:
                self.folder_dict = self.__partial_traversal(self.shared_drive_id, self.root_list[1:])
            else:
                self.folder_dict = self.__full_traversal(self.shared_drive_id)
        else:
            self.folder_dict = self.__full_traversal(self.shared_drive_id)

    def __get_path_info(self, path):

        # get the parts of path
        path_parts = Path(path)

        if '.' in path_parts.name:  # Check if the last part of path is a file
            path_parts = path_parts.parent

        # search the corresponding file id based on the path_parts name
        current_dict = self.folder_dict
        folder_name = 'default'
        folder_id = 'default'
        path_id_name_list = {}
        for path_part in path_parts.parts[1:]:

            if len(current_dict[path_part].keys()) > 1:
                folder_id = current_dict[path_part]["id"]
                folder_name = path_part
                current_dict = {key: value for key, value in current_dict[path_part].items() if key != 'id'}


            else:
                folder_id = current_dict[path_part]["id"]
                folder_name = path_part

        path_id_name_list[folder_name] = {'id': folder_id}

        return path_id_name_list

    def __partial_traversal(self, folder_id, path_list):
        if len(path_list) > 1:
            query = f" '{folder_id}' in parents and name='{path_list[0]}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            results = self.service.files().list(q=query, spaces='drive',
                                                fields='files(id, name)',
                                                supportsAllDrives=True,
                                                includeItemsFromAllDrives=True,
                                                driveId=self.shared_drive_id, corpora='drive'
                                                ).execute()
            items = results.get("files", [])
            folder_dict = {
                items[0]['name']: {
                    'id': items[0]['id'],
                    **self.__partial_traversal(items[0]['id'], path_list[1:])
                }
            }
            return folder_dict
        elif len(path_list) == 1 and folder_id != self.shared_drive_id:
            query = f" '{folder_id}' in parents and name='{path_list[0]}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            results = self.service.files().list(q=query, spaces='drive',
                                                fields='files(id, name)',
                                                supportsAllDrives=True,
                                                includeItemsFromAllDrives=True,
                                                driveId=self.shared_drive_id, corpora='drive'
                                                ).execute()
            items = results.get("files", [])
            temp_dict = {}
            for item in items:
                temp_dict = self.__full_traversal(item['id'])
            return {items[0]['name']: {'id': items[0]['id'], **temp_dict}}
        else:
            query = f" name = '{path_list[0]}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            results = self.service.files().list(q=query, spaces='drive',
                                                fields='files(id, name)',
                                                supportsAllDrives=True,
                                                includeItemsFromAllDrives=True,
                                                driveId=self.shared_drive_id, corpora='drive'
                                                ).execute()
            items = results.get("files", [])
            temp_dict = {}
            for item in items:
                temp_dict = self.__full_traversal(item['id'])
            return {items[0]['name']: {'id': items[0]['id'], **temp_dict}}

    def __full_traversal(self, folder_id):

        query = f" '{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(q=query, spaces='drive',
                                            fields='files(id, name)',
                                            supportsAllDrives=True,
                                            includeItemsFromAllDrives=True,
                                            driveId=self.shared_drive_id, corpora='drive'
                                            ).execute()

        items = results.get("files", [])
        folder_dict = {}
        for item in items:
            folder_id = item['id']
            folder_name = item['name']
            subfolder_dict = self.__full_traversal(folder_id)
            if subfolder_dict != {}:
                folder_dict[folder_name] = {'id': folder_id, **subfolder_dict}
            else:
                folder_dict[folder_name] = {'id': folder_id}
        return folder_dict

    def get_folder_files(self, path):
        # input the path and return the file name and file id
        folder_info = self.__get_path_info(path)
        path_parts = Path(path)
        folder_name = path_parts.name
        folder_id = folder_info[folder_name]['id']
        query = f" '{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(q=query, spaces='drive',
                                            fields='files(id, name)',
                                            supportsAllDrives=True,
                                            includeItemsFromAllDrives=True,
                                            driveId=self.shared_drive_id, corpora='drive'
                                            ).execute()
        items = results.get("files", [])
        return folder_id, items


    def read_folder_files(self, folder_id, items, sheet_name=0):
        try:
            dataframes = {}
            for item in items:
                file_name = item['name']
                output = self.__file_loader(file_name, folder_id, sheet_name)

                for key in output.keys():
                    if file_name in key:
                        dataframes.update(output)
            return dataframes
        except HttpError as error:
            raise f'An error occurred:{error}'
        except Exception as error:
            raise f'An error occurred:{error}'

    def read_file(self, path, sheet_name=0) -> pd.DataFrame:

        folder_info = self.__get_path_info(path)

        path_parts = Path(path)

        folder_name = path_parts.parent.name
        file_name = path_parts.name

        folder_id = folder_info[folder_name]['id']

        # if the last part is file, read the file
        # if len(file_name) > 0:
        file = pd.DataFrame()
        dataframes = self.__file_loader(file_name, folder_id, sheet_name)
        for key in dataframes.keys():
            if file_name in key:
                file = dataframes[key]
        return file

    def rpt_format_file_loader(self, file_name, folder_id, sheet_name=0):
        def read_csv_as_string(result_text):
            csv_text = result_text.replace("\ufeff", "")
            csv_text_list = [
                text for text in csv_text.split("\n") if not text.startswith("(")
            ]
            return csv_text_list
        
        def separate_table(csv_text_list):
            text_list = []
            tmp_text = []
            for text in csv_text_list:
                if text not in ['\r', '']: # 切分辨識用的符號
                    tmp_text.append(f"\n{text}")
                else:
                    text_list.append(tmp_text)
                    tmp_text = []
            text_list = [t for t in text_list if t != []]
            return text_list

        def read_rpt_file_object_as_dataframe(text_list):
            df_dict = {}
            for text in text_list:
                if text:
                    try:
                        table_name = text[2].split(" ")[0].strip().lower()
                        text_file_object = io.StringIO("".join(text))
                        df = pd.read_fwf(text_file_object)[1:]
                        df_dict[table_name] = df
                    except Exception as e:
                        print(e)
                        print(text)
            return df_dict

        print(f"start read: {file_name}")
        # try:
        query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
        results = self.service.files().list(q=query, spaces='drive',
                                            fields='files(id, name)',
                                            supportsAllDrives=True,
                                            includeItemsFromAllDrives=True,
                                            driveId=self.shared_drive_id, corpora='drive'
                                            ).execute()

        items = results.get('files', [])

        # try:
        output = {}
        for item in items:
            if item['name'].endswith(('.xlsx', '.xls', '.csv')):
                file_id = item['id']
                request = self.service.files().get_media(fileId=file_id)
                # 2023/10/31 改變讀檔案方式: 用URL+token
                token = self.creds.token
                url = "https://www.googleapis.com/drive/v3/files/" + file_id + "?alt=media"
                res = requests.get(url, headers={"Authorization": "Bearer " + token})
                res.encoding = res.apparent_encoding  # 'ISO-8859-1' 轉成 'Big5'
                csv_text_list = read_csv_as_string(res.text)
                text_list = separate_table(csv_text_list)
                df_dict = read_rpt_file_object_as_dataframe(text_list)
                for table, data in df_dict.items():
                    output[(file_name, file_id, table)] = data
        return output


    def __file_loader(self, file_name, folder_id, sheet_name=0):
        print(f"start read: {file_name}")

        try:

            query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
            results = self.service.files().list(q=query, spaces='drive',
                                                fields='files(id, name)',
                                                supportsAllDrives=True,
                                                includeItemsFromAllDrives=True,
                                                driveId=self.shared_drive_id, corpora='drive'
                                                ).execute()

            items = results.get('files', [])

        except HttpError as error:
            raise f'An error occurred:{error}'

        try:
            output = {}
            # csv, xlsx, xls
            for item in items:
                if item['name'].endswith(('.xlsx', '.xls', '.csv')):
                    file_id = item['id']
                    request = self.service.files().get_media(fileId=file_id)
                    downloaded = io.BytesIO()
                    downloader = MediaIoBaseDownload(downloaded, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                    downloaded.seek(0)
                    try:
                        if item['name'].endswith('.csv'):
                            df = pd.read_csv(downloaded)
                        else:
                            df = pd.read_excel(downloaded, engine='openpyxl', sheet_name=sheet_name)
                    except:

                        self.read_as_xml(downloaded)
                        df = pd.read_excel("tmp.xlsx", engine="openpyxl", sheet_name=sheet_name)

                    output[(file_name, file_id)] = df

            return output

        except HttpError as error:
            raise f'An error occurred:{error}'
        except Exception as e:
            raise f'An error occurred:{e}'

    def read_as_xml(self, data):
        with ZipFile(data, 'r') as ZIP:
            list_files = ZIP.namelist()
            for f in list_files:
                ZIP.extract(f)
            style_xml = ZIP.read('xl/styles.xml')
            new_style_str = str(style_xml).replace('horizontal="left"', '"horizontal="center"')

            with open("xl/styles_new.xml", "w") as binary_file:
                binary_file.write(new_style_str)
            with ZipFile('tmp.xlsx', mode='w') as zf:
                # 加入要壓縮的檔案
                for f in ZIP.namelist():
                    if f != 'xl/styles.xml':
                        zf.write(f)
                zf.write("xl/styles_new.xml")

    def move_file(self, file_name, old_path, new_path):

        # check folders is existed, create it if not existed
        self.__check_folder_exist(new_path)

        old_path_parts = Path(old_path)
        new_path_parts = Path(new_path)

        old_folder_name = old_path_parts.name
        new_folder_name = new_path_parts.name

        old_path_info = self.__get_path_info(old_path)
        new_path_info = self.__get_path_info(new_path)

        old_folder_id = old_path_info[old_folder_name]['id']
        new_folder_id = new_path_info[new_folder_name]['id']

        print(f"start moving file {file_name} to {new_path}")
        try:
            query = f" name = '{file_name}' and '{old_folder_id}' in parents and trashed = false"
            results = self.service.files().list(q=query, fields='files(id, name)',
                                                supportsAllDrives=True,
                                                includeItemsFromAllDrives=True,
                                                driveId=self.shared_drive_id, corpora='drive').execute()
            items = results.get('files', [])

            file_id = items[0]['id']

            print(f"Moving file: {file_name}")

            self.service.files().update(fileId=file_id,
                                        addParents=new_folder_id,
                                        removeParents=old_folder_id,
                                        fields="id,parents", supportsAllDrives=True).execute()
            print(f"successfully moved file {file_name} to {new_path}")
        except HttpError as error:
            raise f'An error occurred:{error}'
        except Exception as e:
            raise f'An error occurred:{e}'

    def save_to_drive(self, df, file_name, path):

        # check folders is existed, create it if not existed
        self.__check_folder_exist(path)

        folder_info = self.__get_path_info(path)

        path_parts = Path(path)

        folder_name = path_parts.name

        folder_id = folder_info[folder_name]['id']

        file_extension = Path(file_name).suffix

        try:

            if file_extension == ".csv":
                # .csv is textual data so use StringIO
                data_buffer = io.BytesIO()
                df.to_csv(data_buffer, index=False)
                mimetype = 'text/csv'
            elif file_extension in [".xlsx", ".xls"]:
                # .xlsx and .xls are binary data so use BytesIO
                data_buffer = io.BytesIO()
                df.to_excel(data_buffer, index=False, engine='openpyxl')
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                data_buffer = io.BytesIO()
                df.to_excel(data_buffer, index=False, engine='openpyxl')
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        except Exception as e:
            raise f'An error occurred:{e}'

        try:
            # check file if it is existed
            query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
            result = self.service.files().list(q=query, spaces='drive',
                                               fields='files(id, name)',
                                               supportsAllDrives=True,
                                               includeItemsFromAllDrives=True,
                                               driveId=self.shared_drive_id, corpora='drive'
                                               ).execute()
            files = result.get('files', [])

            media = MediaIoBaseUpload(data_buffer, mimetype=mimetype, resumable=True)

            if len(files) > 0:
                file_metadata = {
                    'name': file_name
                }
                # file already exists, update it
                file_id = files[0].get('id')
                print(f"'{file_name}' is existed, update it")
                self.service.files().update(fileId=file_id, body=file_metadata, media_body=media, fields='id',
                                            supportsAllDrives=True).execute()
                print(f"'{file_name}' is updated")
            else:
                file_metadata = {
                    'name': file_name,
                    'parents': [folder_id]
                }
                self.service.files().create(body=file_metadata, media_body=media, fields='id',
                                            supportsAllDrives=True).execute()

                print(f"'{file_name}' is saved")

        except Exception as e:
            raise f'An error occurred:{e}'

    def __check_folder_exist(self, path):

        current_dict = self.folder_dict
        path_parts = Path(path)
        flag = False
        path_id = None

        for path_part in path_parts.parts[1:]:

            if path_part in current_dict:
                if len(current_dict[path_part].keys()) > 1:
                    path_id = current_dict[path_part]['id']
                    current_dict = {key: value for key, value in current_dict[path_part].items() if key != 'id'}

            else:
                flag = True
                parent_id = path_id or current_dict['id']
                file_metadata = {
                    "name": path_part,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_id]
                }
                try:
                    new_folder = self.service.files().create(body=file_metadata, fields="id",
                                                             supportsAllDrives=True).execute()
                    current_dict[path_part] = {"id": new_folder['id']}
                    path_id = None
                    current_dict = current_dict[path_part]
                    print(f"folder {path_part} is not existed and has been created.")
                except HttpError as error:
                    raise f'An error occurred:{error}'

        if flag:
            self.folder_dict = self.__partial_traversal(self.shared_drive_id, self.root_list[1:])
            print("some folders are not existed and have been created.")



