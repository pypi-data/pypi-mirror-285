import argparse
import os
import shutil
from datetime import datetime, timezone
from typing import Union

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import Resource

from .drive_list_files import drive_list_files_with_service
from .emoji_progress_bar import EmojiProgressBar
from .drive_download_metadata import save_drive_download_metadata


def truncate_filename(file_path: str, max_length: int = 80) -> str:
    directory, filename = os.path.split(file_path)
    if len(filename) > max_length:
        extension = os.path.splitext(filename)[1]
        filename = filename[:max_length - len(extension) - 1] + extension
        file_path = os.path.join(directory, filename)
    return file_path


def convert_google_apps_mime_to_office_mime(mime_type: str) -> Union[str, None]:
    mime_mapping = {
        'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    }
    return mime_mapping.get(mime_type, None)


def download_file(service: Resource, file_id: str, file_path: str, modified_time: str, mime_type: str) -> Union[
    str, None]:
    try:
        file_path = truncate_filename(file_path)
        file_path = append_export_extension_to_path(file_path, mime_type)
        export_mime = convert_google_apps_mime_to_office_mime(mime_type)
        if export_mime:
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        else:
            request = service.files().get_media(fileId=file_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        modified_time = datetime.strptime(modified_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        mod_time_stamp = modified_time.timestamp()
        os.utime(file_path, (mod_time_stamp, mod_time_stamp))
        return file_path
    except Exception as e:
        print(f"drive_download.py, an error occurred while downloading the file: {file_path}")
        print(f"error: {e}")


def append_file_extension(file_path: str, mime_type: str) -> str:
    extensions = {
        'application/vnd.google-apps.document': '.docx',
        'application/vnd.google-apps.spreadsheet': '.xlsx',
        'application/vnd.google-apps.presentation': '.pptx'
    }
    return file_path + extensions.get(mime_type, '')


def file_exist(file_path: str, mime_type: str) -> bool:
    updated_file_path = append_file_extension(file_path, mime_type)
    return os.path.exists(updated_file_path)


def append_export_extension_to_path(local_path: str, mime_type: str) -> str:
    return append_file_extension(local_path, mime_type)


def modified_time_match(local_path: str, drive_time: str, mime_type: str) -> bool:
    local_path = append_export_extension_to_path(local_path, mime_type)
    if not os.path.exists(local_path):
        return False
    local_mtime = datetime.fromtimestamp(os.path.getmtime(local_path), tz=timezone.utc)
    drive_mtime = datetime.strptime(drive_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    local_mtime = local_mtime.replace(microsecond=0)
    drive_mtime = drive_mtime.replace(microsecond=0)
    return local_mtime == drive_mtime


def drive_download(service_account_file: str, parent_folder_id: str, max_files: int, output_folder: str = './data',
                   force: bool = False) -> None:
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=credentials)
    print("== Begin listing files in Google Drive ==")
    dic_result = drive_list_files_with_service(service, parent_folder_id, max_files)
    save_drive_download_metadata(dic_result, output_folder)
    items = dic_result['items']
    print("== Begin downloading files from Google Drive ==")
    progress_bar = EmojiProgressBar(len(items))
    current_progress = 0

    download_count = 0
    skip_count = 0
    total_bytes = 0

    for item in items:
        file_path = os.path.join(output_folder, item['path'])
        file_path = truncate_filename(file_path)
        if not force and file_exist(file_path, item['mimeType']) and \
                modified_time_match(file_path, item['modifiedTime'], item['mimeType']):
            skip_count += 1
            current_progress += 1
            progress_bar.update(current_progress)
            continue

        file_path = download_file(service, item['id'], file_path, item['modifiedTime'], item['mimeType'])

        if file_path is not None:
            file_path_txts = f"{file_path}.txts"
            try:
                shutil.rmtree(file_path_txts)
            except FileNotFoundError:
                pass

        download_count += 1
        current_progress += 1
        progress_bar.update(current_progress)
        total_bytes += int(item['size'])

    print(f"Downloaded {download_count} files, total: {total_bytes} bytes, skipped {skip_count} files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files from Google Drive.")
    parser.add_argument('--service_account_file', required=True, type=str,
                        help="Path to the service account credentials file.")
    parser.add_argument('--parent_folder_id', required=True, type=str,
                        help="ID of the Google Drive folder to download contents from.")
    parser.add_argument('--max_files', type=int, default=None, help="Maximum number of files to download.")
    parser.add_argument('--output_folder', type=str, default='./data/農業部20240224',
                        help="Output folder for downloaded files.")
    parser.add_argument('--force', action='store_true', help="Force download even if the file exists locally.")
    args = parser.parse_args()
    drive_download(args.service_account_file, args.parent_folder_id, args.max_files, args.output_folder, args.force)

'''
source venv/bin/activate
python lib_botrun/botrun_ask_folder/drive_download.py \
--service_account_file "./keys/google_service_account_key.json" \
--parent_folder_id "1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9" \
--output_folder "./data/1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9"

'''
