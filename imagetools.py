### Central collection of functions for image downloading and processing ###
### Refactored by Jesse Russell
import platform
import os
import time
import shutil
import requests
import requests_cache
import configparser
import boto3
import pandas as pd
from botocore.exceptions import ClientError
from csv import reader, writer

### Config Setup ###
config = configparser.ConfigParser()
config.read('config.ini')
IMAGE_DIR = config['general']['image_dir']
DEFAULT_WIDTH = config['general']['default_width']
DEFAULT_HEIGHT = config['general']['default_height']
# load AWS settings from config file
REGION = config['aws']['region']
ACCESS_KEY = config['aws']['access_key_id']
SECRET_KEY = config['aws']['secret_access_key']
BUCKET = config['aws']['s3_bucket']
# start global boto3 s3 client
S3_CLIENT = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

### Download Functions ###
def get_image_name(name, sub='-', ext=''):
    # Return a clean image name from an input name
    chars = " &._()|,'\"\\/:"
    for c in chars:
        name = name.replace(c, sub)
        name = name.replace(f'{sub}{sub}', sub).strip(sub)
    name = name.replace(f'{sub}{sub}', sub).strip(sub)
    return f'{name}{ext}'.lower()

def image_ext_or_none(r):
    # verify that the response we've got is actually an image
    content = r.headers['Content-Type'].lower()
    if 'image' in content:
        if 'svg' in content:
            return '.svg'
        else:
            return '.' + content.split('/')[1]  
    return None

# download images from a csv
def download_images(csv_file="sample_image_list.csv",image_dir=IMAGE_DIR,as_png=True):
    requests_cache.install_cache()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0"
    }
    
    # make output directory if it doesn't exist
    os.makedirs(image_dir, exist_ok=True)

    # read the input file
    data = pd.read_csv(csv_file)

    # create local column
    local = []

    # loop through csv
    for row in data.itertuples():
        try:       
            image_url = row.image_url
            if image_url:
                filename = get_image_name(row.filename)
                r = requests.get(image_url, timeout=10, headers=headers)               
                ext = image_ext_or_none(r)
                
                if ext:                                          
                    file_path = os.path.join(image_dir, filename + ext)
                    
                    with open(file_path, 'wb') as f:
                        f.write(r.content)
                    
                    if as_png:
                        if ext != '.png':
                            file_path = change_image_type(file_path, '.png')
                            
                    local.append(file_path)
        except Exception as e:
            local.append(f'ERROR - {e}')
    data["local"] = local
    data.to_csv(csv_file,index=False)

### Processing Functions ###
def process_images(image_dir=IMAGE_DIR,change_type=None,
                   resize=False,width=200,height=200,
                   grayscale=False,padding=False,
                   padding_width=0,padding_height=0,background_color=None):
    # list image directory
    image_files = os.listdir(image_dir)
    # loop through images
    for image in image_files:
        # create filename
        filename = image_dir+"/"+image

        if change_type is not None:
            change_image_type(filename, change_type)

        if resize:
            resize_image(filename, width=width, height=height)

        if padding:
            add_padding(filename, width=padding_width,height=padding_height)

        if grayscale:
            convert_to_grayscale(filename)

        if background_color is not None:
            add_background_color(filename, background_color)        

def change_image_type(name, ext, remove_old=True, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    # Change image type of <name> to ext
    old_name = '.'.join(name.split('.')[:-1])
    old_ext = name.split('.')[-1]
    new_name = f'{old_name}.{ext}'.replace('..', '.')
    if old_ext != ext.strip('.'):
        cmd = f'convert {name} {new_name}'
        # TODO: fix the convert code to work with SVGs 
        # svg files need inkscape
        if old_ext == 'svg':
            # TODO: inkscape doesn't convert SVGs
            cmd = f"inkscape -z -w {width} -h {height} {name} -e {new_name}"
        # webp needs webp
        if old_ext == 'webp':
            cmd = f"dwebp {name} -o {new_name}"

        print(f'\n\nRunning command: \n{cmd}\n')
        os.system(cmd)
        # remove previous image
        if remove_old:
            if os.path.exists(new_name):
                os.system(f'rm {name}')
            else:
                print(f'{name} was not converted')
    return new_name

def get_dominant_color(name):
    base_path = os.path.dirname(name)
    filename = os.path.join(base_path, 'dominant_color.txt')
    cmd = f'convert {name} -scale 50x50! -depth 8 +dither -colors 8 -format \
            "%c" histogram:info:- | sort -r -k 1 | head -n 1 | \
            cut -d")" -f 2 | cut -d" " -f 2 > {filename}'
    os.system(cmd)

    with open(f'{filename}') as file:
        hex = file.read()

    os.system(f'rm {filename}')

    return hex.strip()

def resize_image(name, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    """Resize image to width x height with imagemagick"""
    size = f"{width}x{height}"
    cmd = f'convert {name} -resize {size} {name}'
    os.system(cmd)

def convert_to_grayscale(name):
    """convert image to grayscale with imagemagick"""
    cmd = f'convert {name} -colorspace Gray {name}'
    os.system(cmd)

def add_background_color(name, color):
    """Add background color to image with imagemagick"""
    cmd = f'convert {name} -background {color} -alpha remove -alpha off {name}'
    os.system(cmd)

def add_padding(name, width, height, color=""):
    """Add white padding to the image to the desired --width and --height"""
    if color == "":
        color = get_dominant_color(name)
    size = f"{width}x{height}"
    cmd = f'convert -size {size} xc:{color} {name} -gravity center -composite {name}'
    os.system(cmd)

### S3 Functions ###
# uploads a directory of images to s3
def upload_images(csv_file="sample_image_list.csv",image_dir=IMAGE_DIR,s3_bucket=BUCKET):    
    # upload images to s3 bucket and add image enpoint url to file
    # create bucket if it doesn't exist
    S3_CLIENT.create_bucket(Bucket=s3_bucket, ACL='public-read')

    # read the input file
    data = pd.read_csv(csv_file)

    # create s3 endpoint column
    s3_urls = []

    # loop through csv
    for row in data.itertuples():
        filename = row.local
        if "ERROR" not in filename:
            image = filename.split('/')[1]
            # try to upload the file to s3
            try:
                S3_CLIENT.upload_file(
                    filename, s3_bucket, image,
                    ExtraArgs={'ACL': 'public-read'})
                s3_urls.append(f'https://{s3_bucket}.s3.amazonaws.com/{image}')
            except ClientError as e:
                s3_urls.append(f'ERROR - {e}')
            except FileNotFoundError as e:
                s3_urls.append(f'ERROR - {e}')
        else:
            s3_urls.append('ERROR - not uploaded')
    data["s3_url"] = s3_urls
    data.to_csv(csv_file,index=False)