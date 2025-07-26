import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.core.config import settings

UPLOAD_DIR = Path(settings.UPLOAD_DIR)


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def clean_filename(filename: str) -> str:
    return "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_")).rstrip()


async def save_upload_file(upload_file: UploadFile) -> Path:
    filename = f"{uuid.uuid4().hex}_{clean_filename(upload_file.filename)}"

    file_location = UPLOAD_DIR / filename

    async with aiofiles.open(file_location, "wb") as buffer:
        await buffer.write(await upload_file.read())

    return file_location.resolve()
