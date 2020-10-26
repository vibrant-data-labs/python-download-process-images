#!/usr/bin/env python3

# Import Python Modules

import os
import argparse
import shutil
import time

parser = argparse.ArgumentParser(usage="""
                                 Run various image options on a file or a directory of files.
                                 Files will be backed up by default and then ovwerwritten.
                                 This script uses system commands to perform tasks and has the folowing dependencies:

                                 imagemagick
                                 inkscape for converting svg files to png
                                 webp for converting webp to png

                                 Runs on Linux
                                 """)
parser.add_argument('files', help="single file or directory of image files")
parser.add_argument('--width', help="new image width", default=200)
parser.add_argument('--height', help="new image width", default=200)
parser.add_argument('--f_width', help="new image width", default=200)
parser.add_argument('--f_height', help="new image width", default=200)
parser.add_argument('--pad_color', default=None,
                    help="padding color default dominate color")
parser.add_argument('--resize', action="store_true", default=False,
                    help="resize images to --width and --height")
parser.add_argument('--greyscale', action="store_true", default=False,
                    help="convert images to greyscale")
parser.add_argument('--background-color', default=None,         # IDEA:
                    help="add background color i.e. white")
parser.add_argument('--no-backup', action="store_true", default=False,
                    help="backup original file or directory")
parser.add_argument('--change-type', help="change image type i.e. '.png'")
parser.add_argument('--padding', action="store_true", default=False,
                    help="add white padding to the desired --width and --height")




def change_image_type(name, ext, remove_old=True, width=175, height=175):
    """Change image type of <name> to ext"""
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


def resize_image(name, width=175, height=175):
    """Resize image to width x height with imagemagick"""
    size = f"{width}x{height}"
    cmd = f'convert {name} -resize {size} {name}'
    # print(cmd)
    os.system(cmd)


def convert_to_greyscale(name):
    """convert image to greyscale with imagemagick"""
    base, f_name = os.path.split(name)

    #create new folder for greyscaled
    new_folder = f'{base}_greyscale'

    if not os.path.isdir(new_folder):
        os.system(f'mkdir {new_folder}')

    filename = os.path.join(new_folder, f_name)

    #copy the image first before greyscale
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



if __name__ == '__main__':

    args = parser.parse_args()

    action_options = [
        args.change_type, args.resize, args.greyscale, args.background_color, \
                args.padding
        ]
    action_options = [x for x in action_options if x]
    if not action_options:
        exit('\n\tPlease select one or more actions to perform, -h for options \n')

    # optional backup
    if not args.no_backup:
        try:
            if os.path.isdir(args.files):
                shutil.copytree(args.files, f'{args.files}.bak')
            else:
                shutil.copy(args.files, f'{args.files}.bak')
        except Exception as e:
            print(e)

    if os.path.isdir(args.files):
        image_files = [os.path.join(args.files, x)
                    for x in os.listdir(args.files) if '.' in x]
        print(f'{len(image_files)} images found in {args.files}')

    else:
        image_files = [args.files]

    # allow time for the images to process and resave between actions
    for action in action_options:
        for image in image_files:
            if action == args.change_type:
                change_image_type(image, args.change_type)

            if action == args.resize:
                resize_image(image, width=args.width, height=args.height)

            if action == args.padding:
                add_padding(image, width=args.f_width,
                    height=args.f_height, color=args.pad_color)

            if action == args.greyscale:
                convert_to_greyscale(image)

            if action == args.background_color:
                add_background_color(image, args.background_color)

        time.sleep(5)
