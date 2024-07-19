from fastapi import FastAPI, HTTPException, Query, APIRouter
from fastapi.responses import StreamingResponse, Response
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from urllib.parse import quote

from .util.pdf_util import pdf_page_to_image, DEFAULT_DPI

router = APIRouter(
    prefix='/botrun_ask_folder',
    tags=["botrun_ask_folder"]
)

@router.get("/download_file/{file_id}")
def download_file(file_id: str):
    service_account_file = "keys/google_service_account_key.json"
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=credentials)

    try:
        file = drive_service.files().get(fileId=file_id, fields='name, mimeType').execute()
        file_name = file.get('name')
        file_mime_type = file.get('mimeType')

        request = drive_service.files().get_media(fileId=file_id)

        def file_stream():
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                yield fh.getvalue()
                fh.seek(0)
                fh.truncate(0)

        # Encode the filename for Content-Disposition
        encoded_filename = quote(file_name)

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Content-Type": file_mime_type
        }

        return StreamingResponse(file_stream(), headers=headers, media_type=file_mime_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_pdf_page/{file_id}")
def get_pdf_page(
        file_id: str,
        page: int = Query(1, ge=1, description="Page number to retrieve"),
        dpi: int = Query(DEFAULT_DPI, ge=72, le=600, description="DPI for rendering"),
        scale: float = Query(1.0, ge=0.1, le=2.0, description="Scaling factor"),
        color: bool = Query(True, description="Render in color if True, else grayscale")
):
    try:
        img_byte_arr = pdf_page_to_image(
            file_id=file_id,
            page=page,
            dpi=dpi,
            scale=scale,
            color=color
        )

        return Response(content=img_byte_arr, media_type="image/png")
    except ValueError as e:
        return Response(content=str(e), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
