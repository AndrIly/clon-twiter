import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import close_db, get_db, init_db
from app.middleware.auth import get_current_user
from app.routers import likes_url, posts_url, users_url

from .models import Media

DIST_DIR = Path(__file__).parent.parent / "dist"
UPLOAD_FILE = Path(__file__).parent.parent / "uploads"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    os.makedirs(UPLOAD_FILE, exist_ok=True)
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)
app.include_router(posts_url.router)
app.include_router(likes_url.router)
app.include_router(users_url.router)


@app.post("/api/medias", tags=["medias"])
async def upload_media(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    distinct_name = f"{uuid.uuid4().hex}_{file.filename}"
    content = await file.read()
    file_path = os.path.join(UPLOAD_FILE, distinct_name)

    with open(file_path, "wb") as f:
        f.write(content)

    media = Media(file_name=distinct_name)
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return {"result": True, "media_id": media.id}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_type = exc.__class__.__name__
    error_message = exc.detail
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_type": error_type,
            "error_message": error_message,
            "result": False,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    error_type = exc.__class__.__name__
    error_message = str(exc)
    return JSONResponse(
        status_code=422,
        content={
            "error_type": error_type,
            "error_message": error_message,
            "result": False,
        },
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_type = exc.__class__.__name__
    error_message = str(exc)
    return JSONResponse(
        status_code=500,
        content={
            "error_type": error_type,
            "error_message": error_message,
            "result": False,
        },
    )


# Что это?
if DIST_DIR.exists():
    app.mount("/css", StaticFiles(directory=DIST_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=DIST_DIR / "js"), name="js")
    os.makedirs(UPLOAD_FILE, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_FILE), name="uploads")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse(DIST_DIR / "favicon.ico")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        return FileResponse(DIST_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
