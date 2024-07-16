import argparse
import os
import shutil
from typing import List

from .drive_download_metadata import get_metadata_file_name
from .safe_join import safe_join
from .split_txts import split_txts_no_threads, re_compile_page_number_pattern


def find_files(input_folder: str) -> List[str]:
    splitted_file_pattern = re_compile_page_number_pattern()
    files_list = []
    metadata_file_name = get_metadata_file_name(input_folder)
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file == metadata_file_name:
                continue
            if not splitted_file_pattern.search(file):
                files_list.append(safe_join(root, file))
    return files_list


def run_split_txts(directory: str, chars_per_page: int, force: bool, gen_page_imgs: bool = False) -> None:
    files = find_files(directory)
    output_folders = [f"{file_path}.txts" for file_path in files]
    if force:
        for folder_path in output_folders:
            try:
                shutil.rmtree(folder_path)
            except FileNotFoundError:
                pass
    try:
        split_txts_no_threads(files, output_folders, chars_per_page, force, gen_page_imgs)
    except Exception as e:
        print(f"Error processing files in {directory}")
        print(f"Exception: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="自動掃描目錄並分頁處理文件")
    parser.add_argument("--input_folder", help="要掃描的目錄路徑")
    parser.add_argument("--chars_per_page", type=int, default=2000, help="每頁字符數量")
    parser.add_argument("--force", action='store_true', help="強制重新處理文件，即使已經處理過")
    args = parser.parse_args()

    run_split_txts(args.input_folder, args.chars_per_page, args.force)

'''
source venv/bin/activate
python lib_botrun/botrun_ask_folder/run_split_txts.py \
--input_folder "./data/1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9"

'''
