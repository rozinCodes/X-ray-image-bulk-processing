#!/usr/bin/env python
# coding: utf-8

import os,sys
sys.path.insert(0,"..")
import argparse
from flask import Flask


import subprocess


import csv
import json
from flask import jsonify,request,url_for,send_from_directory
parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, default="", help='')
# parser.add_argument('img_path', type=str)
parser.add_argument('-weights', type=str,default="densenet121-res224-all")
parser.add_argument('-feats', default=False, help='', action='store_true')
parser.add_argument('-cuda', default=False, help='', action='store_true')
parser.add_argument('-resize', default=False, help='', action='store_true')


img_folder_path = '../tests/images/'
dirListing = os.listdir(img_folder_path)
image_formats = [".jpg", ".jpeg", ".png"]
images = [file for file in dirListing if os.path.splitext(file)[1].lower() in image_formats]
app = Flask(__name__)
app.logger.setLevel('ERROR')
app.config['UPLOAD_FOLDER'] = img_folder_path




#user signup api
@app.route('/signup', methods=['POST'])
def signup():
    # Get the user's information from the request
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    
    
    return jsonify({'message': 'User signed up successfully'})


#user signin api
@app.route('/signin', methods=['POST'])
def signin():
    username = request.json['username']
    password = request.json['password']
    
    
    return jsonify({'message': 'User signed in successfully'})




#upload image api
@app.route('/api/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    file_url = url_for('uploaded_file', filename=filename, _external=True)
    return jsonify({'status': 'success', 'file_url': file_url})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)





#csv to json api

@app.route('/', methods=['GET'])
def hello_world():
    jsonArray = []
    file_exists = os.path.isfile(csvFilePath)
    #read csv file
    try:
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
    except:
        print("No Data Found")
        jsonString = {}

    return jsonString

csvFilePath = r'data.csv'
jsonFilePath = r'data.json'



@app.route('/run_script', methods=['GET'])

def run_script():
    subprocess.run(["python", "process_image.py"])


    #     exit()
        # if answers['function'] == 'Bulk image Processing':

        #     if os.path.isfile('data.csv'):
        #         questions = [
        #         inquirer.Confirm("continue", message="Should I continue"),
        # ]

        #         answers = inquirer.prompt(questions)

                
        #     else:
        #         process_image(images.index(answers['image']))





# # if cfg.feats:
# #     print(output)
# # else:
# #     pprint.pprint(output)
    
   
