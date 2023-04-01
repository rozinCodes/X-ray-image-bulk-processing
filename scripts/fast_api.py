import json
import os
import csv
import ast
from fastapi import FastAPI, Request, File, UploadFile, HTTPException, Body
from fastapi.staticfiles import StaticFiles
import subprocess

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



app = FastAPI()

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
ALLOWED_TYPES = set(['Single', 'Multiple'])

@app.post("/api/upload")
async def process_image(request: Request, process_type: str  = Body(...), file: UploadFile = File(...)):
    if process_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="Invalid process type. Only Single and Multiple are allowed.")

    if file.filename.split(".")[-1].lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail="Invalid file type. Only JPG, JPEG, and PNG are allowed.")
        
    # Save uploaded file to disk
    file_path = f"../temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            buffer.write(chunk)

    # Process uploaded file using subprocess
    data = subprocess.run(["python", "api_process.py", file_path], stdout=subprocess.PIPE)
    result = ast.literal_eval(data.stdout.decode('utf-8'))

    # Create URL for uploaded image
    base_url = str(request.base_url)
    image_url = f"{base_url}image/{file.filename}"

    # Return response
    return {"filename": file.filename, "image_url": image_url, "process_type": process_type, "message": "File uploaded successfully.", "data": result}

app.mount("/image", StaticFiles(directory="../temp"))
