#!/usr/bin/env python

from typing import Annotated, IO
from fastapi import FastAPI, File, Header, UploadFile, HTTPException, Form
from pydantic import BaseModel
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
def upload_file(uploaded_file: Annotated[bytes, File()]):
    size_limit = 6 * 1024 *1024
    read_bytes = 0

    UUID = str(uuid4())
    split_UUID = UUID.split('-')
    ID = split_UUID[0]

    for file_bytes in uploaded_file:
        read_bytes += file_bytes
        if read_bytes > size_limit:
            return { "Info": "Uploaded file is too large. Expected file size less than 6MiB" }

    with open(f"{DIR}/{ID}", "wb") as local_file:
        local_file.write(uploaded_file)

    return {"URL": f"Uploaded file can be accessed at http://127.0.0.1:8000/download/{ID}" }

@app.get("/download/{ID}")
def download_file(ID: str):
    return FileResponse(f"{DIR}/{ID}")

