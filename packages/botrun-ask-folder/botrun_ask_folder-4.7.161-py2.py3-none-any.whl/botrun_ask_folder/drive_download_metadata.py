import json
import os
import shutil
from pathlib import Path


def save_drive_download_metadata(dic_item: dict, output_folder: str):
    """
    從 Google Drive 把檔案下載回來的時候，會先將 dic_item 儲存一份
    """
    folder_id = output_folder.split('/')[-1]
    # if folder is not exist, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_path = os.path.join(output_folder, '{folder_id}-metadata.json'.format(folder_id=folder_id))
    # save dict as json, utf-8
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(dic_item, f, ensure_ascii=False, indent=4)


def update_download_metadata(folder_path: str,
                             ori_file_name: str,
                             new_file_name: str, gen_page_imgs: bool = False):
    """
    每次做 txt split 的時候，會把一個檔案分成多個，這時候要更新 metadata
    @param folder_path: 資料夾路徑
    @param ori_file_name: 原始檔案名稱
    @param new_file_name: 切分過後的新檔案名稱
    """
    # 2024-07-13 14:46 bowen to seba , drive_download_metadata.py
    # 發現這邊會有 exception 會讓整個程式碼跳出
    # 異常結束的情況之下會讓分頁程式碼只有分頁一頁就後面跑不完
    # 因此 bowen 加入了 try except 協助除錯完成
    try:
        dic_metadata = get_drive_download_metadata(folder_path)
        file_path = os.path.join(folder_path, get_metadata_file_name(folder_path))
        for item in dic_metadata['items']:
            if item['name'] == ori_file_name:
                new_item = item.copy()
                new_item['name'] = new_file_name
                new_item['gen_page_imgs'] = gen_page_imgs
                new_item['ori_file_name'] = ori_file_name
                if len(new_file_name.split('.')) >= 3 and new_file_name.split('.')[-2].find('page_') != -1:
                    page = new_file_name.split('.')[-2].split('_')[-1]
                    new_item['page_number'] = page
                else:
                    new_item['page_number'] = 'n/a'
                dic_metadata['items'].append(new_item)
                break
        # save dict as json, utf-8
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(dic_metadata, f, ensure_ascii=False, indent=4)
        current_folder_path = Path(__file__).resolve().absolute().parent
        parent_folder_path = current_folder_path.parent
        log_folder_path = parent_folder_path / "users" / "botrun_ask_folder"
        if not log_folder_path.exists():
            log_folder_path.mkdir(parents=True)
        shutil.copy2(file_path, log_folder_path / get_metadata_file_name(folder_path))
    except Exception as e:
        print(f"drive_download_metadata.py, update_download_metadata, exception: {e}")


def get_drive_download_metadata(input_folder: str):
    metadata_path = os.path.join(input_folder, get_metadata_file_name(input_folder))
    if os.path.exists(metadata_path):
        # load json, utf-8
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_metadata_file_name(folder: str):
    folder_id = folder.split('/')[-1]
    return '{folder_id}-metadata.json'.format(folder_id=folder_id)
