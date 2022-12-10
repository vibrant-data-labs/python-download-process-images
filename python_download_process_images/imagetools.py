### Central collection of functions for image downloading and processing ###
### Refactored by Jesse Russell and Eric Berlow
import platform
import os
import time
import shutil
import requests
#import requests_cache
import configparser
import boto3
import pandas as pd
from cairosvg import svg2png
from botocore.exceptions import ClientError
import mimetypes
from csv import reader, writer
import pathlib as pl

### Config Setup ###
config = configparser.ConfigParser()
wd = pl.Path.cwd() 
configpath = wd/'config.ini'
if configpath.exists():
    config.read(configpath)

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
else:
    IMAGE_DIR = None
    DEFAULT_WIDTH = 0
    DEFAULT_HEIGHT = 0
    BUCKET = None

##############################
###   Download Functions   ###
##############################

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
    try:
        content = r.headers['Content-Type'].lower()
        if 'image' in content:
            if 'svg' in content:
                return '.svg'
            else:
                return '.' + content.split('/')[1]  
        return None
    except:
        return None

# download images from a csv
def download_images(csv_file="sample_image_list.csv",image_dir=IMAGE_DIR,as_png=True):
    #requests_cache.install_cache()
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
    
    
# download images from pandas dataframe
def download_images_df(df, image_dir=IMAGE_DIR,as_png=True):
    '''
    description: 
        download images from image url to local folder 
        and add new column with path/filename to the local image file
        the dataframe must have columns 'name' and 'image_url'
    ----------
    Parameters:
    df : datafrane with columns 'name', 'image_url' 
    image_dir : local directory where to download images
    as_png : if true will convert all images to png
    ----------
    Returns: dataframe with new column of local image filename

    '''
    
    #requests_cache.install_cache()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0"
    }
    
    print("downloading images to local directory")
    # make output directory if it doesn't exist
    os.makedirs(image_dir, exist_ok=True)

    d = {} # dictionary to hold results {name:filename} pairs
    e = {} # dictonary to hold errors {name:error} pairs

    # loop through dataframe
    for row in df.itertuples():
        print("downloading image for %s" %row.name)
        try:       
            image_url = row.image_url
            if image_url and image_url.startswith('http'):
                filename = get_image_name(row.name)
                r = requests.get(image_url, timeout=10, headers=headers)               
                ext = image_ext_or_none(r)

                if ext:                                          
                    file_path = os.path.join(image_dir, filename + ext)
                    
                    with open(file_path, 'wb') as f:
                        f.write(r.content)
                    
                    if as_png:
                        if ext != '.png':
                            if ext == '.svg':
                                file_path = change_image_type(file_path, '.png')
                                svg2png(url=image_url, write_to=file_path)
                            else:
                                file_path = change_image_type(file_path, '.png')
                            
                    d[row.name] = file_path
                    e[row.name] = ""
                else:
                    d[row.name] = ""
                    e[row.name] = "FileExtensionError"
            else:
                d[row.name] = ""
                e[row.name] = "ImageUrlError"            
        except:
            d[row.name]=""
            e[row.name] = "ImageDownloadError"      
    df['filename'] = df['name'].map(d) # map filename value to name as new column in dataframe
    df['filename'].fillna("", inplace=True)
    df['error'] = df['name'].map(e) # map error value to name as new column in dataframe
    df['error'].fillna("", inplace=True)
    
    # remove rows that have no filepath or error name
    error_rows = df.apply(lambda x: (x['filename'] == "") or (x['error'] in ["FileExtensionError", "ImageUrlError", "ImageDownloadError"]), axis=1)
    df_success = df[~error_rows].reset_index(drop=True)
    # create a dataframe of the error
    df_failures = df[error_rows].reset_index(drop=True)
    
    return df_success, df_failures

##############################
### Processing Functions ###
##############################

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
        # if old_ext == 'svg':
            # TODO: inkscape doesn't convert SVGs
            # cmd = f"inkscape -z -w {width} -h {height} {name} -e {new_name}"
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


##############################
### S3 Functions ###
##############################

# uploads a directory of images to s3 from csv file
def upload_images(csv_file="sample_image_list.csv",image_dir=IMAGE_DIR,s3_bucket=BUCKET):    
    '''
    upload images to s3 bucket and add image enpoint url to file    
    '''

    print("uploading images to AWS s3 budket: %s" %s3_bucket)
    # create bucket if it doesn't exist
    S3_CLIENT.create_bucket(Bucket=s3_bucket, ACL='public-read')

    # read the input file
    data = pd.read_csv(csv_file)

    # create s3 endpoint column
    s3_urls = []

    # loop through csv
    for row in data.itertuples():
        filename = row.filename
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


# upload a directory of images to s3 from dataframe
def upload_images_df(df,image_dir=IMAGE_DIR,s3_bucket=BUCKET):    
    '''
    Description:  
        upload images to s3 bucket
        create bucket if it doesn't exist
        add column to dataframe with image endpoint url
    ----------
    Parameters:
        df : pandas dataframe with columns "name", "filename"
        image_dir : directory path of local image files to upload
        s3_bucket : name of s3 bucket where to upload images.

    Returns: dataframe with extra column of s3 endpoint url

    '''
    print("uploading images to s3")
    
    S3_CLIENT.create_bucket(Bucket=s3_bucket, ACL='public-read')

    # create s3 endpoint column
    s3_urls_dict = {} # dictionary to hold results {name: s3_url}

    # loop through dataframe
    for row in df.itertuples():
        print("uploading image for %s to s3 bucket: %s " %(row.name, s3_bucket))
        filename = row.filename
        mime_type = mimetypes.guess_type(filename)[0] # detect image type (png, jpg, svg, etc)
        if "ERROR" not in filename: # double check no other errors to skip
            image = filename.split('/')[-1]
            # try to upload the file to s3
            try:
                S3_CLIENT.upload_file(
                    filename, s3_bucket, image,
                    ExtraArgs={'ACL': 'public-read', # make the endpoint public
                                'ContentType': mime_type}) #  image type necessary for display instead of download 
                s3_urls_dict[row.name]= (f'https://{s3_bucket}.s3.amazonaws.com/{image}')
            except ClientError as e:
                s3_urls_dict[row.name]=(f'ERROR - {e}')
            except FileNotFoundError as e:
                s3_urls_dict[row.name]=(f'ERROR - {e}')
        else:
            s3_urls_dict[row.name]=('ERROR - not uploaded')
    df["s3_url"] = df['name'].map(s3_urls_dict) # map filename value to name as new column in dataframe
    df['s3_url'].fillna("", inplace=True)
    return df
    

##################################
### Example test script
##################################
    
if __name__ == '__main__':
   image_directory = "data/images"
   # read file  - doesn't matter if it's csv or excel.
   # note - data must have must have these column names 'name', 'image_url', 'filename'
   df = pd.read_excel('data/LinkedIn_Test.xlsx', engine='openpyxl') # subset columns with image name and url
   df['filename'] = df['name']

   
   image_url_file = 'data/LinkedIn_test.csv'
   df.to_csv(image_url_file, index=False)

   '''
   # download images to local directory and update dataframe with filename column
   download_images(csv_file=image_url_file, image_dir=image_directory, as_png=True) # convert all to png if possible

   # process all images in the local directory (e.g. resize, convert to grey)
   process_images(image_dir=image_directory, resize=True,width=200,height=200,
                          grayscale=True,padding=False,
                          padding_width=100,padding_height=100)
   
   # upload images in the local directory to s3 and update dataframe with s3 endpoint
   upload_images(csv_file=image_url_file, image_dir=image_directory)
   '''

   #############################################################
   ### below is to process from pandas dataframe, not csv ###
 
   # download images to local directory and update dataframe with filename column, plus return separate errors dataframe
   df, error_rows = download_images_df(df, image_dir=image_directory, as_png=True) # convert all to png if possible

   # process all images in the local directory (e.g. resize, convert to grey)
   process_images(image_dir=image_directory, resize=True,width=200,height=200,
                          grayscale=True,padding=False,
                          padding_width=100,padding_height=100)
   
   # upload images in the local directory to s3 and update dataframe with s3 endpoint
   df = upload_images_df(df, image_dir=image_directory)


   # add original column names and s3 url cleaned of errors
   #df['id'] = df['name']
   df['Logo_URL'] = df['s3_url'].apply(lambda x: "" if "ERROR" in x else x) # replace error messages with empty string
   #df = df[['id','name', 'Logo_URL']] # cleaned dataset final columns to keep
   
   # write processed file with added columns
   df.to_excel('data/LinkedIn_Test_Processed.xlsx', index=False, encoding = 'utf-8-sig')