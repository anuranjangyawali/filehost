#!/usr/bin/env python

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from typing import Annotated
from uuid import uuid4

app = FastAPI()

DIR="storage"
UUID=str(uuid4())

@app.get("/")
async def root():
    return { "Message": "This is the API for my filehost."}

@app.post("/upload")
async def upload_file(uploaded_file: UploadFile):
    with open(f"{DIR}/{UUID}", "wb") as wfile:
        content = await uploaded_file.read()
        wfile.write(content)
    return {"URL": f"{uploaded_file.filename} can be accessed at /download/{UUID}" }

@app.get("/download/{UUID}")
async def download_file(UUID: str):
    return FileResponse(f"{DIR}/{UUID}")
    




