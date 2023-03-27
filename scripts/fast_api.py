from typing import Union

import json
import os
import csv
from fastapi import FastAPI, File, UploadFile
import os
import uuid


app = FastAPI()


@app.get("/")
def receive_list():
    jsonArray = []
    
    file_exists = os.path.isfile(csvFilePath)
    try:
    #     if file_exists:
    #         return jsonString
    #     else:
        with open(csvFilePath, encoding='utf-8') as csvf: 
            csvReader = csv.DictReader(csvf) 

            for row in csvReader: 
                jsonArray.append(row)

        with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
            jsonString = json.dumps(jsonArray, indent=4)
            jsonf.write(jsonString)
        os.remove(jsonFilePath)
    except Exception as e:
        print(e)
        jsonString = {"message": "No Data Found"}

    return jsonString
csvFilePath = r'../processed_data/data.csv'
jsonFilePath = r'../processed_data/data.json'

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



@app.post("/api/upload")
async def process_image(file: UploadFile = File(...)):
    ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
    if file.filename.split(".")[-1].lower() not in ALLOWED_EXTENSIONS:
        return {"error": "Invalid file type. Only JPG, JPEG, and PNG are allowed."}

    # processed_image = None

    # if processed_image is None:
    #     return {"error": "Invalid processing type."}
    file_path = f"../temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            buffer.write(chunk)
    external_url = app.url_path_for(file.filename)

    return {"filename": file.filename, "file_path": external_url, "message": "File uploaded successfully."}


# @app.post("/api/upload")
# async def root(file: UploadFile = File(...)):
#     file_path = f"../temp/{file.filename}"
#     with open(file_path, "wb") as buffer:
#         while True:
#             chunk = await file.read(1024)
#             if not chunk:
#                 break
#             buffer.write(chunk)
#     return {"filename": file.filename, "file_path": file_path, "message": "File uploaded successfully."}
