#!/usr/bin/env python

import os
import asyncio
from datetime import date
from typing import Annotated
from fastapi import FastAPI, File, Form 
from fastapi.responses import FileResponse
from uuid import uuid4
from pydantic import BaseModel

app = FastAPI()
DIR="storage"
item_db: list[dict] = []
response: list[dict] = []

@app.on_event("startup")
async def startup():
    asyncio.create_task(delete_files())

async def delete_files():
    while True:
        print(item_db)
        await asyncio.sleep(86400)

def size_check(files, file_no):
    size_limit = 6291456
    read_bytes = 0
    for file_bytes in files[file_no]:
        read_bytes += file_bytes
        if read_bytes >= size_limit:
            return f"Uploaded file no {file_no} is too large."
    return files[file_no]

def file_metadata():
    UUID = str(uuid4())
    split_UUID = UUID.split('-')
    ID = split_UUID[0]
    DATE = date.today()
    return ID,DATE

@app.get("/")
def root():
    return { "Message": "This is the API for my filehost."}

@app.get("/list")
def list_files():
    list_of_files = os.listdir(DIR)
    return {"ID": list_of_files}

@app.post("/upload")
def upload_file(files: Annotated[list[bytes], File(title="Upload File", \
                description="Upload file size less than 6MiB")],
                expire_after: Annotated[int, Form(\
                description="Expire in x days")] = 1):

    ID, DATE = file_metadata()
    print(ID)

    for file_no in range(len(files)):
        file = size_check(files, file_no)

        if type(file) is str:
            response.append(file)
        else:
            with open(f"{DIR}/{ID}", "wb") as local_file:
                item_db.append({ID : { "Expire-after": expire_after, "Created-on": DATE  } }) 
                local_file.write(files[file_no])
                response.append(f"Uploaded file no {file_no} can be accessed at http://127.0.0.1:8000/download/{ID}")

    return { "URLs": response, "No of files uploaded": len(files), "Expire in (days)": expire_after }

@app.get("/download/{ID}")
def download_file(ID: str):
    return FileResponse(f"{DIR}/{ID}")


