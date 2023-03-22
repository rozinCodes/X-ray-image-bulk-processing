import os,sys
sys.path.insert(0,"..")
import argparse
import skimage, skimage.io


import torch
import torch.nn.functional as F
import torchvision, torchvision.transforms
import torchxrayvision as xrv
import pandas as pd
import inquirer



parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, default="", help='')
parser.add_argument('-weights', type=str,default="densenet121-res224-all")
parser.add_argument('-feats', default=False, help='', action='store_true')
parser.add_argument('-cuda', default=False, help='', action='store_true')
parser.add_argument('-resize', default=False, help='', action='store_true')


img_folder_path = '../images/'
dirListing = os.listdir(img_folder_path)
image_formats = [".jpg", ".jpeg", ".png"]
images = [file for file in dirListing if os.path.splitext(file)[1].lower() in image_formats]




if len(images) >= 1:

    questions = [inquirer.List('function','Which function do you want to run? (Make sure to place your image files in images/)',
    choices=['Bulk image Processing', 'Single image process'], default='Bulk image Processing',
                        carousel=True)]
    answers = inquirer.prompt(questions)
else:
    print("No images found in images/")
    exit()

# function to process image

def process_image(i):
    print(f"{images[i]} currently at position {i + 1} out of {len(images)}")
    cfg = parser.parse_args()


    headerShow = False if i > 0 else True

    img = skimage.io.imread(f"{img_folder_path}/{images[i]}")

    img = xrv.datasets.normalize(img, 255)  


    # Check that images are 2D arrays
    if len(img.shape) > 2:
        img = img[:, :, 0]
    if len(img.shape) < 2:
        print("error, dimension lower than 2 for image")
        

    # Add color channel
    img = img[None, :, :]


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
        
        df["Filename"] = images[i]
        df.insert(0, 'Filename', df.pop('Filename'))
        df.to_csv('../processed_data/data.csv',mode='a', index=False, header=None if headerShow == False else True)
    
    
if answers['function'] == 'Bulk image Processing':
    if os.path.isfile('../processed_data/data.csv'):
        questions = [
        inquirer.Confirm("continue", message="There is already a data.csv file Do you want to append to the existing file?", default=False),
    ]

        answers = inquirer.prompt(questions)
        if answers['continue'] == False:
            os.remove('../processed_data/data.csv')
    for i in range(len(images)):
        process_image(i)
    print("Done")
else:
    
    questions = [inquirer.List('image','on which image do you want to run your analysis?',
    choices=images, default=images[0],
                    carousel=True)]
    answers = inquirer.prompt(questions)
    process_image(images.index(answers['image']))
    



