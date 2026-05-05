#!/usr/bin/env python

import os
from typing import Annotated
from fastapi import FastAPI, File
from fastapi.responses import FileResponse
from uuid import uuid4

app = FastAPI()

DIR="storage"

def size_check(files, file_no):
    size_limit = 6291456
    read_bytes = 0
    for file_bytes in files[file_no]:
        read_bytes += file_bytes
        if read_bytes >= size_limit:
            return f"Uploaded file no {file_no} is too large."
    return files[file_no]

def item_id():
    UUID = str(uuid4())
    split_UUID = UUID.split('-')
    ID = split_UUID[0]
    return ID

@app.get("/")
def root():
    return { "Message": "This is the API for my filehost."}

@app.get("/list")
def list_files():
    list_of_files = os.listdir(DIR)
    return list_of_files

@app.post("/upload")
def upload_file(files: Annotated[list[bytes], File(title="Upload File", description="Upload file size less than 6MiB")]):
    ID = item_id()
    response = []
    for file_no in range(len(files)):
        file = size_check(files, file_no)

        if type(file) is str:
            response.append(file)
        else:
            with open(f"{DIR}/{ID}", "wb") as local_file:
                local_file.write(files[file_no])
                response.append(f"Uploaded file no {file_no} can be accessed at http://127.0.0.1:8000/download/{ID}")

    return { "URLs": response, "No of files uploaded:": len(files)}


@app.get("/download/{ID}")
def download_file(ID: str):
    return FileResponse(f"{DIR}/{ID}")

