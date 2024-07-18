# shaku_data_util

## 內容
所有關於資料庫處理、google drive 資料處理、GCS處理

## 用途分類：
1. API 內部使用
2. 普通branch ： 給其他三個repo 使用，所以如果有更新，需要上傳pypi
  
## 檔案層級：
- `api` : 只在develop_api 、release_api 兩條branchs，內部使用的api工具
- `database` : 各個資料庫的工具程式
- `gdrive_gcs_toolkit` : google drive 工具程式
- `prod_cloudbuild.yaml` : cloud build yaml 檔，觸發prod cloud build 後會執行的script，只有 api branch會用到
- `setup.py` : 讓程式知道資料層級script
- `requirements.txt` : 需要的 pip packages
- `app.py` : 只有在api branch裏面，api 主程式

## Branchs
- `release`
  - prod 環境
  - 無cloud build
- `develop`
  - dev 環境
  - 無 cloud build
- `staging`
  - 不屬於任何環境
  - 無 cloud build
- `release_api`
  - api prod 環境
  - 有 cloud build
- `develop_api`
  - api dev 環境
  - 無 cloud build

## shaku_data_util 上傳 pypi 流程

1. 開發完成或是修改完成
2. 切回 develop
3. 在 setup.py 中 ， update version
4. 在 repo 目錄下執行 
   ```
   python setup.py sdist bdist_wheel
   ```
5. 接著執行
   ```
   // 已不支援 account password
   twine upload  --skip-existing dist/*

   twine upload --config-file=D:\Shaku\data-util\.pypirc --skip-existing dist/*
   ```
7. 輸入 pypi 帳密
   - account：shaku_algo
   - password ：shakualgoai
8. 上傳完畢
9. 若 cloud run container 沒有重新佈板，需要手動重佈
