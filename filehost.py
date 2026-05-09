#!/usr/bin/env python

import os
import asyncio
import time
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Form 
from fastapi.responses import FileResponse
from uuid import uuid4
from pydantic import BaseModel

app = FastAPI()
DIR="storage"
file_db: list[dict] = []
response: list[dict] = []

@app.on_event("startup")
async def startup():
    asyncio.create_task(delete_files())

async def delete_files():
    while True:
        if len(file_db) > 0:
            for outer_dict in file_db:
                for values in outer_dict.values():
                    set_expire_day = values["Expire-after"]
                    set_creation_time = values["Uploaded-on"]
                    if time.time() > set_creation_time + set_expire_day * 86400:
                        ID = list(outer_dict.keys())
                        index_num = file_db.index(outer_dict)
                        os.remove(f"{DIR}/{ID[0]}")
                        file_db.__delitem__(index_num)
        await asyncio.sleep(5)

def size_check(files, file_no):
    size_limit = 6291456
    read_bytes = 0
    for file_bytes in  files[file_no].file:
        read_bytes += len(file_bytes)
        if read_bytes >= size_limit:
            return f"Uploaded file no {file_no} is too large."
    files[file_no].file.seek(0)
    return files[file_no].file

def file_metadata():
    UUID = str(uuid4())
    split_UUID = UUID.split('-')
    ID = split_UUID[0]
    TIME = time.time()
    return ID,TIME


@app.get("/")
def root():
    return { "Message": "This is the API for my filehost."}

@app.get("/list")
def list_files():
    list_of_files = os.listdir(DIR)
    return {"ID": list_of_files}

@app.post("/upload")
def upload_file(files: Annotated[list[UploadFile], File(title="Upload File", \
                description="Upload file size less than 6MiB")],\
                expire_after: Annotated[int, Form(\
                description="Expire in x days")] = 1):


    for file_no in range(len(files)):
        ID, TIME = file_metadata()
        file = size_check(files, file_no)

        if type(file) is str:
            response.append(file)
        else:
            with open(f"{DIR}/{ID}", "wb") as local_file:
                file_db.append({ID : { "Expire-after": expire_after, "Uploaded-on": TIME } }) 
                local_file.write(file.read())
                response.append(f"Uploaded file no {file_no} can be accessed at http://127.0.0.1:8000/download/{ID}")

    return { "URLs": response, "No of files uploaded": len(files), "Expire in (days)": expire_after }

@app.get("/download/{ID}")
def download_file(ID: str):
    return FileResponse(f"{DIR}/{ID}")


