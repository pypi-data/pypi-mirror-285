import asyncio
import os
import shutil

# from .botrun_ask_folder_logger import BotrunAskFolderLogger
from .botrun_drive_manager import botrun_drive_manager
from .drive_download import drive_download
from .embeddings_to_qdrant import embeddings_to_qdrant
from .run_split_txts import run_split_txts
from .run_pdf_to_img import run_pdf_to_img


def botrun_ask_folder(google_drive_folder_id: str,
                      force=False,
                      gen_page_imgs=False
                      ) -> None:
    """
    @param google_drive_folder_id: Google Drive folder ID
    @param force: If True, 所有的資料 (qdrant collection, downloaded files...) 會刪掉重新建立
    """
    # 不要加 logger，前台會一直印東西
    # logger.info(f"Starting botrun_ask_folder for folder ID: {google_drive_folder_id}")
    # BotrunAskFolderLogger().get_logger().debug(f"Starting botrun_ask_folder for folder ID: {google_drive_folder_id}")

    if force:
        if os.path.exists(f"./data/{google_drive_folder_id}"):
            # logger.info(f"Removing existing data directory for folder ID: {google_drive_folder_id}")
            shutil.rmtree(f"./data/{google_drive_folder_id}")

    google_service_account_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS",
                                                "/app/keys/google_service_account_key.json")
    # BotrunAskFolderLogger().get_logger().debug(f"Downloading files from Google Drive folder ID: {google_drive_folder_id}")
    drive_download(
        google_service_account_key_path,
        google_drive_folder_id,
        9999999,
        output_folder=f"./data/{google_drive_folder_id}",
        force=force,
    )

    # BotrunAskFolderLogger().get_logger().debug(f"Splitting text files in directory: {google_drive_folder_id}")
    run_split_txts(
        f"./data/{google_drive_folder_id}",
        2000,
        force,
        gen_page_imgs)

    if gen_page_imgs:
        run_pdf_to_img(google_drive_folder_id, force)

    qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port = os.getenv("QDRANT_PORT", 6333)
    # BotrunAskFolderLogger().get_logger().debug(f"Starting embeddings to Qdrant for folder ID: {google_drive_folder_id}")
    asyncio.run(embeddings_to_qdrant(
        f"./data/{google_drive_folder_id}",
        "openai/text-embedding-3-large",
        3072,
        30,
        f"{google_drive_folder_id}",
        qdrant_host,
        qdrant_port,
        force=force
    ))

    # logger.info(f"Running botrun_drive_manager for folder ID: {google_drive_folder_id}")
    botrun_drive_manager(
        f"波{google_drive_folder_id}",
        f"{google_drive_folder_id}",
        force=force)
