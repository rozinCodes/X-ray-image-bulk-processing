#!/usr/bin/env python
# coding: utf-8

import os,sys
sys.path.insert(0,"..")
import argparse
from flask import Flask
# from process_image import process_image
import ast
import subprocess
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import csv
import json
from flask import jsonify,request,url_for,send_from_directory
from flask_restful import Api, Resource
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from typing import Optional
import re


img_folder_path = '../temp/'
app = Flask(__name__)
api = Api(app)
CORS(app)
app.logger.setLevel('ERROR')
app.config['UPLOAD_FOLDER'] = img_folder_path

def get_db():
    conn = psycopg2.connect(
        host="localhost",
        database="Users",
        user="postgres",
        password="1234"
    )
    return conn


@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')

        if not username:
            return jsonify({'message': 'Username is required'})
        if not email:
            return jsonify({'message': 'Email is required'})
        if not password:
            return jsonify({'message': 'Password is required'})
        if len(password) < 8:
            return jsonify({'message': 'Password must be at least 8 characters'})
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'message': 'Please enter a valid email address'})

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT users FROM users WHERE username=%s OR email=%s", (username, email))
        result = cur.fetchone()

        if result:
            cur.close()
            conn.close()
            return jsonify({'message': 'User already exists'})

        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred while processing the request'}), 500

    return jsonify({'message': 'User signed up successfully'})


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    result = cur.fetchone()

    if result is None:
        return jsonify({'message': 'Invalid username or password'})

    if check_password_hash(result[2], password):
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid username or password'})




#upload image api
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No image file provided.'}), 400

    if 'process_type' not in request.form:
        return jsonify({'message': 'No process type provided.'}), 400
    file = request.files['file']
    process_type = request.form['process_type']
    filename = file.filename
    
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    data = subprocess.run(["python", "api_process.py", f"../temp/{filename}"],stdout=subprocess.PIPE)
    
    file_url = url_for('uploaded_file', filename=filename, _external=True)
    return jsonify({'status': 'success','message': 'Image processed successfully','process_type': process_type, 'file_url': file_url, 'data': ast.literal_eval(data.stdout.decode('utf-8'))})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)





#csv to json api

@app.route('/', methods=['GET'])
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



@app.route('/run_script', methods=['GET'])

def run_script():
    subprocess.run(["python", "process_image.py"])


# # if cfg.feats:
# #     print(output)
# # else:
# #     pprint.pprint(output)
    
   
