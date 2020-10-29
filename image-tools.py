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
from botocore.exceptions import ClientError
from csv import reader, writer

### Config Setup ###
config = configparser.ConfigParser()
config.read('config.ini')
IMAGE_DIR = config['general']['image_dir']
DEFAULT_WIDTH = config['general']['default_width']
DEFAULT_HEIGHT = config['general']['default_height']

### S3 Functions ###
# initializes s3 by retrieving credentials and returns s3 api object
def init_s3():
    sts = boto3.client('sts')
    ACCESS_KEY = config['s3']['aws_access_key_id']
    SECRET_KEY = config['s3']['aws_secret_access_key']
    SESSION_TOKEN = sts.get_session_token()
    s3 = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN
    )
    return s3
# uploads an image to the specified s3 bucket
def upload_file(s3_client, file_name, bucket, object_name=None):
    ### Upload a file to an S3 bucket
    #
    # :param file_name: File to upload
    # :param bucket: Bucket to upload to
    # :param object_name: S3 object name. If not specified then file_name is used
    # :return: True if file was uploaded, else False
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return False
    return True

### Setup Functions ###
# install local image tool dependencies
def install_tools():
    if platform.system() == "Linux": linux()
    if platform.system() == "Darwin": darwin()
    if platform.system() == "Windows": print(">> Windows is not supported.")
    if platform.system() == "": print(">> Not recognized.")
def linux():
    # install dependencies via apt (will only work for ubuntu)
    os.system('sudo apt install libcanberra-gtk-module python3-pip python3 imagemagick inkscape webp -y')
    os.system('python3 -m pip install -r requirements.txt')
def darwin():
    # install dependencies via brew (homebrew must be installed)
    os.system('brew install python imagemagick inkscape webp')
    os.system('python3 -m pip install -r requirements.txt')

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
def download_images(csv_file="sample_image_list.csv",uploadToS3=no_header=False):
    requests_cache.install_cache()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0"
    }
    output_data = []

    # make output directory if it doesn't exist
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # read the input file
    with open(csv_file) as f:
        data = [x for x in reader(f)]

    # remove the first row if it's a header
    if not no_header:
        output_data.append(data.pop(0))

    for line in data:
        try:       
            image_url = line[1]
            if image_url:
                filename = get_image_name(line[2])
                r = requests.get(image_url, timeout=10, headers=headers)               
                ext = image_ext_or_none(r)
                
                if ext:                                          
                    file_path = os.path.join(IMAGE_DIR, filename + ext)
                    
                    with open(file_path, 'wb') as f:
                        f.write(r.content)
                    line.append(file_path)
                else:
                    line.append(f'{r.status_code} - Image not available')
            output_data.append(line)
        except Exception as e:
            print(e)        
    # resave .csv file with our additional column            
    name, ext = csv_file.split('.')
    outfile = f'{name}_processed.{ext}'
    with open(outfile, 'w') as f:
        mywriter = writer(f)
        for line in output_data:
            mywriter.writerow(line)

### Processing Functions ###
def change_image_type(name, ext, remove_old=True, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    # Change image type of <name> to ext
    old_name = '.'.join(name.split('.')[:-1])
    old_ext = name.split('.')[-1]
    new_name = f'{old_name}.{ext}'.replace('..', '.')
    if old_ext != ext.strip('.'):
        cmd = f'convert {name} {new_name}'

        # svg files need inkscape
        if old_ext == 'svg':
            cmd = f"inkscape -z -w {width} -h {height} {name} -e {new_name}"

        # webp needs webp
        if old_ext == 'webp':
            cmd = f"dwebp {name} -o {new_name}"

        print(f'\n\nRunning command: \n{cmd}\n')
        os.system(cmd)
        # remove previous image
        if remove_old:
            # input('Enter..')
            time.sleep(5)
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
    # print(cmd)
    os.system(cmd)


def convert_to_grayscale(name):
    """convert image to grayscale with imagemagick"""
    base, f_name = os.path.split(name)

    #create new folder for grayscale
    new_folder = f'{base}_grayscale'

    if not os.path.isdir(new_folder):
        os.system(f'mkdir {new_folder}')

    filename = os.path.join(new_folder, f_name)

    #copy the image first before grayscale
    #shutil.copyfile(name, filename)

    cmd = f'convert {name} -colorspace Gray {filename}'
    os.system(cmd)

def add_background_color(name, color):
    """Add background color to image with imagemagick"""
    cmd = f'convert {name} -background {color} -alpha remove -alpha off {name}'
    # print(cmd)
    os.system(cmd)

def add_padding(name, width, height, color=""):
    """Add white padding to the image to the desired --width and --height"""

    if not color:
        color = get_dominant_color(name)

    size = f"{width}x{height}"
    cmd = f'convert -size {size} xc:{color} {name} -gravity center -composite {name}'
    # print(cmd)
    os.system(cmd)