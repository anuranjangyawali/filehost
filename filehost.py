#!/usr/bin/env python

from typing import Annotated, IO
from fastapi import FastAPI, File, Header, UploadFile, HTTPException
from uuid import uuid4
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from starlette import status

app = FastAPI()

DIR="storage"

@app.get("/")
def root():
    return { "Message": "This is the API for my filehost."}

@app.post("/upload")
def upload_file(uploaded_file: UploadFile, content_length: Annotated[int | None, Header(lt=6*1024*1024)]):
    UUID=str(uuid4())
    total_size_limit = 6 * 1024 *1024
    chunk_size = 0

    for chunk in uploaded_file.file:
        chunk_size += len(chunk)
        if chunk_size > total_size_limit:
            return { "Info": "Uploaded file is too large. Expected file size less than 6MiB"}

    with open(f"{DIR}/{UUID}", "wb") as wfile:
        content = uploaded_file.file.read()
        wfile.write(content)
    return {"URL": f"Uploaded file can be accessed at /download/{UUID}" }

@app.get("/download/{UUID}")
def download_file(UUID: str):
    return FileResponse(f"{DIR}/{UUID}")

