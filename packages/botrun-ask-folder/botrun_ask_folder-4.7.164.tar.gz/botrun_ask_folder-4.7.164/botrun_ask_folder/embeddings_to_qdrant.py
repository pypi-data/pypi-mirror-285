import argparse
import asyncio
import dotenv
import os
import qdrant_client
import uuid
import json
from litellm import aembedding, embedding
from pathlib import Path
from qdrant_client.http import models

from botrun_ask_folder.remove_qdrant_collection import remove_collection_with_client
from .drive_download_metadata import get_drive_download_metadata, get_metadata_file_name
from .create_qdrant_collection import create_collection_with_client
from .emoji_progress_bar import EmojiProgressBar
from .split_txts import get_page_number_prefix

dotenv.load_dotenv()


async def is_already_indexed(client, collection_name, text_content):
    try:
        search_response = await client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="text_content",
                        match=models.MatchValue(value=text_content)
                    ),
                ]
            ),
            limit=1
        )
        return len(search_response[0]) > 0
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 發生例外錯誤，參數如下：\n- client: {client}\n- collection_name: {collection_name}\n- text_content: {text_content}")
        print(f"embeddings_to_qdrant.py, 錯誤訊息：{e}")
        # 異常處理後，假設資料不存在
        return False


async def index_document(client, collection_name, document_data_payload, embeddings):
    try:
        await client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    payload=document_data_payload,
                    vector=embeddings,
                )
            ]
        )
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 上傳文件發生錯誤，參數如下：\n- client: {client}\n- collection_name: {collection_name}\n- document_data_payload: {document_data_payload}\n- embeddings: {embeddings}")
        print(f"embeddings_to_qdrant.py, 錯誤訊息：{e}")


DEFAULT_MAX_TEXT_ONE_PAGE = 5200


def generate_embedding_sync(model, texts):
    try:
        if len(texts) > DEFAULT_MAX_TEXT_ONE_PAGE:
            texts = texts[:DEFAULT_MAX_TEXT_ONE_PAGE]
        embedding_result = embedding(model=model, input=texts)
        return embedding_result
    except Exception as e:
        print(f"embeddings_to_qdrant.py, 生成嵌入發生錯誤，參數如下：\n- model: {model}\n- texts: {texts}")
        print(f"embeddings_to_qdrant.py, 錯誤訊息：{e}")
        return {'data': [{'embedding': []}]}


async def generate_embedding_async(model, texts):
    try:
        # if texts len > DEFAULT_MAX_TEXT_ONE_PAGE, cut it
        if len(texts) > DEFAULT_MAX_TEXT_ONE_PAGE:
            texts = texts[:DEFAULT_MAX_TEXT_ONE_PAGE]
        embedding = await aembedding(model=model, input=texts)
        return embedding
    except Exception as e:
        print(f"embeddings_to_qdrant.py, 生成嵌入發生錯誤，參數如下：\n- model: {model}\n- texts: {texts}")
        print(f"embeddings_to_qdrant.py, 錯誤訊息：{e}")
        # 返回一個空的嵌入結果以避免中斷流程
        return {'data': [{'embedding': []}]}


async def process_file(client, file_path, collection_name, model, semaphore, counters, progress_bar, dic_metadata={}):
    async with semaphore:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            if await is_already_indexed(client, collection_name, text_content):
                counters['skipped_count'] += 1
            else:
                embeddings_response = await generate_embedding_async(model, [f'{file_path} {text_content}'])
                embeddings = embeddings_response['data'][0]['embedding']

                document_data_payload = {
                    "text_content": text_content,
                    "file_path": str(file_path)
                }
                if dic_metadata:
                    for item in dic_metadata['items']:
                        if item['name'] == file_path.name:
                            document_data_payload['google_file_id'] = item['id']
                            document_data_payload['gen_page_imgs'] = item['gen_page_imgs']
                            document_data_payload['ori_file_name'] = item['ori_file_name']
                            if 'page_number' in item.keys() and item['page_number'] != 'n/a':
                                document_data_payload['page_number'] = item['page_number']
                            break

                await index_document(client, collection_name, document_data_payload, embeddings)
                counters['added_count'] += 1
            progress_bar.update(counters['skipped_count'] + counters['added_count'])
        except Exception as e:
            print(f"embeddings_to_qdrant.py, 處理文件發生錯誤，文件路徑：{file_path}")
            print(f"embeddings_to_qdrant.py, 錯誤訊息：{e}")


def count_txt_files(input_folder):
    total_files = 0
    try:
        for _, _, files in os.walk(input_folder):
            for file in files:
                if get_page_number_prefix() in file:
                    total_files += 1
    except Exception as e:
        print(f"embeddings_to_qdrant.py, 計算文件數目發生錯誤，資料夾路徑：{input_folder}")
        print(f"embeddings_to_qdrant.py, 錯誤訊息：{e}")
    return total_files


async def embeddings_to_qdrant(input_folder, model, dimension, max_tasks,
                               collection_name, qdrant_host, qdrant_port, force=False):
    try:
        client = qdrant_client.AsyncQdrantClient(qdrant_host, port=qdrant_port)
        if force:
            await remove_collection_with_client(client, collection_name)
        semaphore = asyncio.Semaphore(max_tasks)
        await create_collection_with_client(client, collection_name, dimension)

        counters = {'skipped_count': 0, 'added_count': 0}
        tasks = []
        # print start this process
        print("== Starting the embedding to Qdrant ==")
        progress_bar = EmojiProgressBar(count_txt_files(input_folder))
        int_txt_files_count = 0
        metadata_file_name = get_metadata_file_name(input_folder)
        dic_metadata = get_drive_download_metadata(input_folder)
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file == metadata_file_name:
                    continue
                if get_page_number_prefix() in file:
                    file_path = Path(root) / file
                    task = process_file(client, file_path, collection_name, model, semaphore, counters, progress_bar,
                                        dic_metadata)
                    tasks.append(task)
                    int_txt_files_count += 1

        await asyncio.gather(*tasks)
        print(f"embeddings_to_qdrant_txt.py, "
              f"skipped: {counters['skipped_count']}, "
              f"added to qdrant: {counters['added_count']}")
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 處理資料夾發生錯誤，參數如下：\n- input_folder: {input_folder}\n- model: {model}\n- dimension: {dimension}\n- max_tasks: {max_tasks}\n- collection_name: {collection_name}\n- qdrant_host: {qdrant_host}\n- qdrant_port: {qdrant_port}")
        print(f"embeddings_to_qdrant.py, 錯誤訊息：{e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index documents into Qdrant with embeddings.")
    parser.add_argument("--input_folder", default="./data")
    parser.add_argument("--model", default="openai/text-embedding-3-large")
    parser.add_argument("--dimension", type=int, default=3072)
    parser.add_argument("--max_tasks", type=int, default=30)
    parser.add_argument("--collection_name", type=str, default="collection_3")
    parser.add_argument("--qdrant_host", type=str, default=None)  # 新增參數
    parser.add_argument("--qdrant_port", type=int, default=None)  # 新增參數
    args = parser.parse_args()
    # 如果指定了命令列參數，則使用它們；否則從環境變數或使用默認值
    qdrant_host = args.qdrant_host if args.qdrant_host is not None else os.getenv('QDRANT_HOST', 'localhost')
    qdrant_port = args.qdrant_port if args.qdrant_port is not None else int(os.getenv('QDRANT_PORT', '6333'))
    try:
        asyncio.run(
            embeddings_to_qdrant(args.input_folder, args.model, args.dimension, args.max_tasks, args.collection_name,
                                 qdrant_host, qdrant_port))
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 主程序發生錯誤，參數如下：\n- input_folder: {args.input_folder}\n- model: {args.model}\n- dimension: {args.dimension}\n- max_tasks: {args.max_tasks}\n- collection_name: {args.collection_name}\n- qdrant_host: {qdrant_host}\n- qdrant_port: {qdrant_port}")
        print(f"embeddings_to_qdrant.py, 錯誤訊息：{e}")

'''
source venv/bin/activate
python lib_botrun/botrun_ask_folder/embeddings_to_qdrant.py \
--input_folder "./data/1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9" \
--model "openai/text-embedding-3-large" \
--dimension 3072 \
--collection_name "1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9" \
--qdrant_host "localhost" \
--qdrant_port 6333
'''
