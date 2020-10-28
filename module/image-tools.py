### Central collection of functions for image downloading and processing ###
### Refactored by Jesse Russell
import platform
import os
import time
import shutil
import requests
import requests_cache
from csv import reader, writer

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
def download_images(csv_file="sample_image_list.csv",image_dir="downloaded_images",url_prefix="",no_header=False):
    requests_cache.install_cache()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0"
    }
    output_data = []

    # make output directory if it doesn't exist
    os.makedirs(image_dir, exist_ok=True)

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
                    file_path = os.path.join(image_dir, filename + ext)
                    
                    with open(file_path, 'wb') as f:
                        f.write(r.content)
                    if ext != '.png':
                        old_file_path = file_path
                        file_path = change_image_type(file_path, '.png')
                        time.sleep(2)
                    if url_prefix:
                        file_path = url_prefix + file_path
                    line.append(file_path)
                else:
                    line.append(f'{r.status_code} - Image not available')
            output_data.append(line)
        except KeyboardInterrupt:
            exit('exiting...')
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
def change_image_type(name, ext, remove_old=True, width=175, height=175):
    # Change image type of <name> to ext
    old_name = '.'.join(name.split('.')[:-1])
    old_ext = name.split('.')[-1]
    new_name = f'{old_name}.{ext}'.replace('..', '.')
    if old_ext != ext.strip('.'):
        cmd = f'convert {name} {new_name}'

        # svg files need inscape
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