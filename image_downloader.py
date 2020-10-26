#!/usr/bin/env python3
from csv import reader, writer
import argparse
import os
import logging
import time

import requests
import requests_cache
from image_processor import change_image_type, resize_image, convert_to_greyscale, add_background_color
from html_from_csv import html_from_data

log = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    filename='log',
                    format='%(asctime)s | %(levelname)s %(module)s.%(funcName)s %(lineno)d- %(message)s',
                    filemode='w')



parser = argparse.ArgumentParser()
parser.add_argument('file', 
                    help="""csv file must match the following layout:\n
                    Organization | Logo URL | Filename
                    """)
parser.add_argument('--dir', help="dir for downloaded files - will be created",
                    default="downloaded_images")
parser.add_argument('--no_header', help="set if .csv file doesn't have a header row",
                    default=False, action="store_true")
parser.add_argument('--url-prefix', default="https://openmappr-images.sfo2.digitaloceanspaces.com/",
                    help="The url to prepend to the logo links")
args = parser.parse_args()


requests_cache.install_cache()


def get_image_name(name, sub='-', ext=''):
    """Return a clean image name from an input name"""
    chars = " &._()|,'\"\\/:"
    for c in chars:
        name = name.replace(c, sub)
        name = name.replace(f'{sub}{sub}', sub).strip(sub)
    name = name.replace(f'{sub}{sub}', sub).strip(sub)
    return f'{name}{ext}'.lower()


def image_ext_or_none(r):
    """verify that the response we've got is actually an image"""
    content = r.headers['Content-Type'].lower()
    if 'image' in content:
        if 'svg' in content:
            return '.svg'
        else:
            return '.' + content.split('/')[1]  
    return None
            
        
headers = {
    "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0"
}
output_data = []

# make output directory if it doesn't exist
os.makedirs(args.dir, exist_ok=True)

# read the input file
with open(args.file) as f:
    data = [x for x in reader(f)]
    
# remove the first row if it's a header
if not args.no_header:
    output_data.append(data.pop(0))
    
for line in data:
    try:       
        image_url = line[1]
        if image_url:
            filename = get_image_name(line[2])
            r = requests.get(image_url, timeout=10, headers=headers)               
            ext = image_ext_or_none(r)
            
            if ext:                                          
                file_path = os.path.join(args.dir, filename + ext)
                
                with open(file_path, 'wb') as f:
                    f.write(r.content)
                    
                if ext != '.png':
                    old_file_path = file_path
                    file_path = change_image_type(file_path, '.png')
                    log.info(f'File was changed from {old_file_path} to {file_path}')
                    time.sleep(2)
                
                log.info(f'image found for {line[0]}')
                if args.url_prefix:
                    file_path = args.url_prefix + file_path
                line.append(file_path)
                # resize_image(file_path)
                # add_background_color(file_path, 'white')
                # convert_to_greyscale(file_path)                    
                # print(f'{i+1}: {file_path}')
                
            else:
                log.info(f'#{line[0]}  {r.status_code} - Image not available')
                line.append(f'{r.status_code} - Image not available')
        
        else:
            log.info(f'no image url for #{line[0]}')
                    
        output_data.append(line)

    except KeyboardInterrupt:
        exit('exiting...')

    except Exception as e:
        print(e)
            
# resave .csv file with our additional column            
name, ext = args.file.split('.')
outfile = f'{name}_processed.{ext}'

with open(outfile, 'w') as f:
    mywriter = writer(f)
    for line in output_data:
        mywriter.writerow(line)
        
if not args.no_header:
    output_data.pop(0)
html_from_data('image-table.html', output_data)

