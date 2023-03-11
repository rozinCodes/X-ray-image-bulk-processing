
# This repo is a fork of the  [TorchXRayVision](https://github.com/mlmed/torchxrayvision) 📝  



Clone the project  

#I used Python 3.8 64 bit version and pip version 23.0.1

~~~bash 
git clone https://github.com/rozinCodes/X-ray-image-bulk-processing.git
~~~

~~~bash
pip install -r requirements.txt
~~~

Place some image(s) in the test/images folder

~~~bash
cd scripts
~~~

Run the image process
~~~bash
python process_image.py
~~~

There will be a prompt asking you to select if you want to process a single image or process mutiple images together

If you select Bulk image processing, images in the test/images/ folder will be processed and the results will be stored in scripts folder in a csv file called data.csv
There is an option to choose from images when selecting single image processing.

