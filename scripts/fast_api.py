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
    #read csv file
    try:
    #     if file_exists:
    #         return jsonString
    #     else:
        with open(csvFilePath, encoding='utf-8') as csvf: 
            #load csv file data using csv library's dictionary reader
            csvReader = csv.DictReader(csvf) 

            #convert each csv row into python dict
            for row in csvReader: 
                #add this python dict to json array
                jsonArray.append(row)

        #convert python jsonArray to JSON String and write to file
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
async def process_image(processed_type: str, file: UploadFile = File(...)):
    ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
    if file.filename.split(".")[-1].lower() not in ALLOWED_EXTENSIONS:
        return {"error": "Invalid file type. Only JPG, JPEG, and PNG are allowed."}

    processed_image = None
    # Add more processing types here

    if processed_image is None:
        return {"error": "Invalid processing type."}

    filename = str(uuid.uuid4())
    extension = file.filename.split(".")[-1].lower()
    save_path = os.path.join("processed_images", f"{filename}.{extension}")
    with open(save_path, "wb") as f:
        f.write(processed_image)

    return {"url": f"/processed_images/{filename}.{extension}"}