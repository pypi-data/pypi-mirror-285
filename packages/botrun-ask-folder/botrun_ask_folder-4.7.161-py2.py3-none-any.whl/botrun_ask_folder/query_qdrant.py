import argparse
import os
import re
import sys
import json
from datetime import datetime
from litellm import completion
from qdrant_client import QdrantClient
from qdrant_client.http import models

from botrun_ask_folder.generate_pages_html import generate_pdf_gallery_html
from .embeddings_to_qdrant import generate_embedding_sync

DEFAULT_NOTICE_PROMPT = '''
妳是臺灣人，回答要用臺灣繁體中文正式用語不能輕浮、不能隨便 
請妳不可以使用簡體中文回答，不可以使用大陸慣用語回答 
請妳基於「知識庫」及使用者的提問，step by step 分析之後，列點（要有標題與內容）回答 
若「知識庫」有談到相關的時間、數字、數據，務必一定要講出來，才精確，不能省略！ 
若「知識庫」有談到舉例、案例、故事、示範，務必一定要用例子回答，才能懂，不能省略！ 
若「知識庫」有時間或日期，而文字內容相似矛盾的話，要用最新時間日期的為準，別用舊的
如果妳不會回答的部分，不可以亂猜

回答的最後面請幫我加上
<<Botrun.ai波特人的沉穩參考來源>>
下面接一個JSON，格式為：
{
    "references":[]
}
references裡的資料，是依據你回答的內容所參考的「知識庫」內容，格式為：
{
    "ori_file_name":"",
    "page_number:"",
    "google_file_id":"",
    "gen_page_imgs":"",
    "collection_name":""
 }
ori_file_name 的內容，請參考「知識庫」回傳的 ori_file_name tag 內的結果，如果辨別不出來，就放空字串
page_number 的內容，請參考「知識庫」回傳的 page_number tag 內的結果，只要放數字，如果辨別不出數字，就放空字串
google_file_id 的內容，請參考「知識庫」回傳的 google_file_id tag 內的結果，如果辨別不出來，就放空字串
gen_page_imgs 的內容，請參考「知識庫」回傳的 gen_page_imgs tag 內的結果，可能會是 True, False 或是空字串，如果辨別不出來，就放空字串

如果回答時有參考多個「知識庫」的內容，請依序列加在 references 的 array 裡面

因此整個回答的範例會為：
原本要回答的內容

<<Botrun.ai波特人的沉穩參考來源>>
{
    "references":[
    {
        "ori_file_name":"filename.pdf",
        "page_number:"2",
        "google_file_id":"123456ABC",
        "gen_page_imgs":"True",
        "collection_name":"collection_1"
     }
    ]
}
'''

SPECIAL_STRING = "<<Botrun.ai波特人的沉穩參考來源>>"


def query_qdrant_knowledge_base(qdrant_host,
                                qdrant_port,
                                collection_name,
                                user_input,
                                embedding_model,
                                top_k,
                                hnsw_ef,
                                file_path_field='file_path',
                                text_content_field='text_content',
                                google_file_id_field='google_file_id',
                                page_number_field='page_number',
                                gen_page_imgs_field='gen_page_imgs',
                                ori_file_name_field='ori_file_name',
                                ) -> str:
    qdrant_client_instance = QdrantClient(qdrant_host, port=qdrant_port)
    query_vector = generate_embedding_sync(embedding_model, user_input)
    search_params = models.SearchParams(hnsw_ef=hnsw_ef, exact=False)
    search_result = qdrant_client_instance.search(
        collection_name=collection_name,
        query_vector=query_vector['data'][0]['embedding'],
        search_params=search_params,
        limit=top_k,
        with_payload=True,
        with_vectors=True
    )

    str_knowledge_base = ""
    # fastapi_url = os.environ.get('FAST_API_URL', 'http://localhost:8000')
    pdf_list = []
    for idx, hit in enumerate(search_result, start=1):
        google_file_id = hit.payload.get(google_file_id_field, '')
        page_number = hit.payload.get(page_number_field, '')
        ori_file_name = hit.payload.get(ori_file_name_field, '')
        gen_page_imgs = hit.payload.get(gen_page_imgs_field, False)
        str_knowledge_base += (f"\n"
                               f"<a-rag-file>\n"
                               f"<file-path>\n"
                               f"{hit.payload.get(file_path_field, 'N/A')}\n"
                               f"</file-path>\n")
        str_knowledge_base += (f"<google_file_id>"
                               f"{google_file_id}"
                               f"</google_file_id>\n")
        str_knowledge_base += (f"<page_number>"
                               f"{page_number}"
                               f"</page_number>\n")
        str_knowledge_base += (f"<ori_file_name>"
                               f"{ori_file_name}"
                               f"</ori_file_name>\n")
        str_knowledge_base += (f"<gen_page_imgs>"
                               f"{gen_page_imgs}"
                               f"</gen_page_imgs>\n")
        str_knowledge_base += (f"<collection_name>"
                               f"{collection_name}"
                               f"</collection_name>\n")

        # if google_file_id:
        #     str_knowledge_base += (f"<原始檔案連結>"
        #                            f"{api_prefix}/download_file/{google_file_id}"
        #                            f"</原始檔案連結>\n")
        # if page_number and page_number.lower() != 'n/a':
        #     str_knowledge_base += (f"<page-number>\n"
        #                            f"{page_number}\n"
        #                            f"</page-number>\n")
        # if google_file_id and page_number and page_number.lower() != 'n/a' and gen_page_imgs:
        #     pdf_list.append({
        #         "filename": f"{hit.payload.get(ori_file_name_field, 'N/A')}",
        #         "page": page_number,
        #         "image_url": f"/api/data/{collection_name}/img/{google_file_id}_{page_number}.png",
        #         # "image_url": f"https://sizeinfotool.com/images/a4%E7%B4%99%E5%BC%B5%E5%B0%BA%E5%AF%B8%E5%A4%A7%E5%B0%8F.png",
        #         "pdf_url": f"{api_prefix}/download_file/{google_file_id}"
        #     })
        str_knowledge_base += (f"<text-content>\n"
                               f"{hit.payload.get(text_content_field, 'N/A')}"
                               f"</text-content>\n"
                               f"</a-rag-file>\n"
                               )
    # if len(pdf_list) > 0:
    #     os.makedirs(f"./data/{collection_name}/html", exist_ok=True)
    #     now = datetime.now().strftime("%Y%m%d%H%M%S")
    #     open(f"./data/{collection_name}/html/index{now}.html", "w").write(generate_pdf_gallery_html(pdf_list))
    #     str_knowledge_base += (f"<page-ref>"
    #                            f"/api/data/{collection_name}/html/index{now}.html"
    #                            f"</page-ref>"
    #                            )
    os.makedirs("./users/botrun_ask_folder", exist_ok=True)
    open("./users/botrun_ask_folder/str_knowledge_base.txt", "w").write(str_knowledge_base)
    return str_knowledge_base


# def save_pdf_page_to_image(google_file_id, page_number):
#     os.makedirs("./users/botrun_ask_folder/img", exist_ok=True)
#     filename = f"./users/botrun_ask_folder/img/{google_file_id}_{page_number}.png"
#     if not os.path.exists(filename):
#         img_byte_arr = pdf_page_to_image(google_file_id, int(page_number))
#         with open(filename, "wb") as f:
#             f.write(img_byte_arr)

def query_qdrant_and_llm(qdrant_host, qdrant_port, collection_name, user_input,
                         embedding_model, top_k, notice_prompt,
                         chat_model, hnsw_ef, file_path_field,
                         text_content_field, google_file_id_field,
                         page_number_field, gen_page_imgs_field, ori_file_name_field):
    str_knowledge_base = query_qdrant_knowledge_base(
        qdrant_host, qdrant_port, collection_name, user_input,
        embedding_model, top_k, hnsw_ef, file_path_field, text_content_field,
        google_file_id_field, page_number_field, gen_page_imgs_field, ori_file_name_field)
    if not notice_prompt:
        notice_prompt = DEFAULT_NOTICE_PROMPT
    str_message = f'''
    <知識庫RAG搜索到的內容>
    {str_knowledge_base}
    </知識庫RAG搜索到的內容>

    <回答時請妳注意>
    {notice_prompt}
    </回答時請妳注意>

    <使用者提問請妳回答>
    {user_input}
    </使用者提問請妳回答>
    '''
    return completion_call(chat_model, str_message)


def completion_call(model, message):
    try:
        messages = [{"content": message, "role": "user"}]
        generator = filtered_stream_with_hidden_content(model, messages)
        reference_content = ""
        # 迭代生成器直到倒數第二個值
        for chunk in generator:
            if isinstance(chunk, str):  # 確保chunk是字符串
                # print(chunk, end='', flush=True)
                if chunk.startswith(SPECIAL_STRING):
                    reference_content = chunk.split(SPECIAL_STRING, 1)[1]
                    break
                yield chunk
            else:
                break  # 如果chunk不是字符串，跳出循環

        # print("\n\nHidden content:")
        # print(reference_content)
        try:
            lst_refs = json.loads(reference_content)['references']
            generated_ref_page = generate_pdf_page_to_image(lst_refs)
            yield generate_ref_section(lst_refs, generated_ref_page)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
    except Exception as e:
        # print stacktrace
        import traceback
        traceback.print_exc()
        print(f"query_qdrant.py, completion_call, exception: {e}")


def generate_ref_section(lst_refs, generated_ref_page:bool):
    api_prefix = '/api/botrun/botrun_ask_folder'
    ref_files_id = {}
    ref_files_and_page = {}
    for ref in lst_refs:
        if ref['ori_file_name'] in ref_files_and_page.keys():
            current_pages = ref_files_and_page[ref['ori_file_name']]
            if ref['page_number'] not in current_pages:
                ref_files_and_page[ref['ori_file_name']].append(ref['page_number'])
        else:
            ref_files_and_page[ref['ori_file_name']] = [ref['page_number']]
        if ref['google_file_id'] not in ref_files_id.keys():
            ref_files_id[ref['ori_file_name']] = ref['google_file_id']
    ref_text = "參考來源："
    for file_name, pages in ref_files_and_page.items():
        google_file_id = ref_files_id[file_name]
        ref_text += f"\n- [{file_name} 第{', '.join(pages)}頁](" + f"{api_prefix}/download_file/{google_file_id}" + ")"
    if generated_ref_page:
        ref_text += f"\n- [參考頁面截圖](/api/data/{lst_refs[0]['collection_name']}/html/index{datetime.now().strftime('%Y%m%d%H%M%S')}.html)"
    return ref_text


def generate_pdf_page_to_image(lst_refs):
    api_prefix = '/api/botrun/botrun_ask_folder'
    pdf_list = []
    for ref in lst_refs:
        google_file_id = ref.get('google_file_id', '')
        page_number = ref.get('page_number', '')
        ori_file_name = ref.get('ori_file_name', '')
        gen_page_imgs = ref.get('gen_page_imgs', False)
        # if gen_page_imgs is string, convert to boolean
        if isinstance(gen_page_imgs, str):
            gen_page_imgs = gen_page_imgs.lower() == 'true'
        if not gen_page_imgs:
            continue
        collection_name = ref.get('collection_name', '')
        if google_file_id and page_number and page_number.lower() != 'n/a' and gen_page_imgs:
            pdf_list.append({
                "filename": f"{ori_file_name}",
                "page": page_number,
                "image_url": f"/api/data/{collection_name}/img/{google_file_id}_{page_number}.png",
                "pdf_url": f"{api_prefix}/download_file/{google_file_id}"
            })
    if len(pdf_list) > 0:
        os.makedirs(f"./data/{collection_name}/html", exist_ok=True)
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        open(f"./data/{collection_name}/html/index{now}.html", "w").write(generate_pdf_gallery_html(pdf_list))
        return True
    return False


def filtered_stream_with_hidden_content(model, messages):
    response = completion(model=model, messages=messages, stream=True)
    buffer = ""
    hidden_content = ""
    found_special_string = False

    for chunk in response:
        content = chunk.choices[0].delta.content or ""
        buffer += content

        if not found_special_string:
            # 檢查是否包含特殊字符串
            split = buffer.split(SPECIAL_STRING, 1)

            if len(split) > 1:
                # 如果找到特殊字符串
                yield split[0]  # 只輸出特殊字符串之前的內容
                hidden_content += split[1]  # 開始收集隱藏內容
                found_special_string = True
                buffer = ""
            else:
                # 如果沒有找到特殊字符串，檢查是否可以安全地yield一部分buffer
                safe_to_yield = re.search(r'(.*\S+\s+)', buffer)
                if safe_to_yield:
                    to_yield = safe_to_yield.group(1)
                    yield to_yield
                    buffer = buffer[len(to_yield):]
        else:
            # 特殊字符串之後的所有內容都添加到hidden_content
            hidden_content += content

    # 如果整個響應結束都沒有找到特殊字符串，yield剩餘的buffer
    if buffer and not found_special_string:
        yield buffer

    # 最後yield隱藏內容
    yield SPECIAL_STRING + hidden_content.strip()


def query_qdrant_and_llm_print(qdrant_host, qdrant_port, collection_name, user_input,
                               embedding_model, top_k, notice_prompt,
                               chat_model, hnsw_ef, file_path_field, text_content_field,
                               google_file_id_field='google_file_id', page_number_field='page_number',
                               gen_page_imgs_field='gen_page_imgs', ori_file_name_field="ori_file_name"
                               ):
    for fragment in query_qdrant_and_llm(qdrant_host, qdrant_port, collection_name, user_input,
                                         embedding_model, top_k, notice_prompt,
                                         chat_model, hnsw_ef, file_path_field, text_content_field,
                                         google_file_id_field, page_number_field, gen_page_imgs_field,
                                         ori_file_name_field):
        print(fragment, end="")
        sys.stdout.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search documents in Qdrant using natural language query.")
    parser.add_argument("--query")
    parser.add_argument("--collection", default="collection_1")
    parser.add_argument("--embedding_model", default="openai/text-embedding-3-large")
    parser.add_argument("--top_k", default=12)
    parser.add_argument("--notice_prompt", default=DEFAULT_NOTICE_PROMPT)
    parser.add_argument("--chat_model", default="gpt-4-turbo-preview")
    parser.add_argument("--hnsw_ef", default=256)
    parser.add_argument("--file_path_field", default="file_path")
    parser.add_argument("--text_content_field", default="text_content")
    args = parser.parse_args()

    qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
    qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
    query_qdrant_and_llm_print(qdrant_host, qdrant_port, args.collection, args.query,
                               args.embedding_model, args.top_k,
                               args.notice_prompt, args.chat_model,
                               args.hnsw_ef, args.file_path_field,
                               args.text_content_field,
                               )
