#!/usr/bin/env python
# coding: utf-8

import os,sys
sys.path.insert(0,"..")
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import argparse
import skimage, skimage.io
from flask import Flask


import torch
import torch.nn.functional as F
import torchvision, torchvision.transforms
import subprocess


import torchxrayvision as xrv
import pandas as pd
import inquirer
import csv
import json
import requests
from flask import jsonify,request,url_for,send_from_directory
parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, default="", help='')
# parser.add_argument('img_path', type=str)
parser.add_argument('-weights', type=str,default="densenet121-res224-all")
parser.add_argument('-feats', default=False, help='', action='store_true')
parser.add_argument('-cuda', default=False, help='', action='store_true')
parser.add_argument('-resize', default=False, help='', action='store_true')


img_folder_path = '../images/'
dirListing = os.listdir(img_folder_path)
image_formats = [".jpg", ".jpeg", ".png"]
images = [file for file in dirListing if os.path.splitext(file)[1].lower() in image_formats]
app = Flask(__name__)
app.logger.setLevel('DEBUG')
app.config['UPLOAD_FOLDER'] = img_folder_path



if len(images) >= 1:

    questions = [inquirer.List('function','Which function do you want to run? (Make sure to place your image files in images/)',
    choices=['Bulk image Processing', 'Single image process'], default='Bulk image Processing',
                        carousel=True)]
    answers = inquirer.prompt(questions)
else:
    print("No images found in images/")

#function to process image
def process_image(i):
    print(f"{images[i]} currently at position {i + 1} out of {len(images)}")


    headerShow = False if i > 0 else True
    print(images[i])
    img = skimage.io.imread(f"{img_folder_path}/{images[i]}")
    img = xrv.datasets.normalize(img, 255)  


    # Check that images are 2D arrays
    if len(img.shape) > 2:
        img = img[:, :, 0]
    if len(img.shape) < 2:
        print("error, dimension lower than 2 for image")

    # Add color channel
    img = img[None, :, :]
    cfg = parser.parse_args()


    # the models will resize the input to the correct size so this is optional.
    if cfg.resize:
        transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),
                                                    xrv.datasets.XRayResizer(224)])
    else:
        transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop()])

    img = transform(img)


    model = xrv.models.get_model(cfg.weights)

    output = {}
    with torch.no_grad():
        img = torch.from_numpy(img).unsqueeze(0)
        if cfg.cuda:
            img = img.cuda()
            model = model.cuda()
            
        if cfg.feats:
            feats = model.features(img)
            feats = F.relu(feats, inplace=True)
            feats = F.adaptive_avg_pool2d(feats, (1, 1))
            output["feats"] = list(feats.cpu().detach().numpy().reshape(-1))

        preds = model(img).cpu()
        output["preds"] = dict(zip(xrv.datasets.default_pathologies,preds[0].detach().numpy()))

        df = pd.DataFrame(data=output['preds'].values(), index=output['preds'].keys() if headerShow else None,)
        df = (df.T)
        
        df["Filename"] = [images[i]]
        df.insert(0, 'Filename', df.pop('Filename'))
        df.to_csv('../processed_data/data.csv',mode='a', index=False, header=None if headerShow == False else True)

if answers['function'] == 'Bulk image Processing':
    for i in range(len(images)):
        process_image(i)
    print("Done")
else:
    
    questions = [inquirer.List('image','on which image do you want to run your analysis?',
    choices=images, default=images[0],
                    carousel=True)]
    answers = inquirer.prompt(questions)
    process_image(images.index(answers['image']))
    



