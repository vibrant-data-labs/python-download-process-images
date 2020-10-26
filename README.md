# Python Download and Processing Image Scripts
1. Download or clone this repository: `git clone https://github.com/ericberlow/python-download-process-images.git`
2. Change to this project's directory in your terminal: `cd python-download-process-images`

## Install dependencies
> macOS
1. Run `brew install python imagemagick inkscape webp`
3. Run `python3 -m pip install -r requirements.txt`
> Ubuntu
2. Run `sudo apt-get install libcanberra-gtk-module python3-pip python3 imagemagick inkscape webp -y`
3. Run `python3 -m pip install -r requirements.txt`

## Dependencies

- **imagemagick:** used for image conversions.
- **inkscape:** used for converting SVG to PNG files.
- **webp:** used for converting webp to PNG

## Use:

1. Run `bash download_and_process.sh sample_image_list.csv` to run the 
	- **download images** which downloads the images and converts to png
	- **image processing** script converts to grayscale and 175x175 px.
	- **html from csv** which creates a table of company names and logos, so you can spot check them if you have hundreds.

* Or run `python3 image_downloader.py sample_image_list.csv` if you just want to download images
* Or run `python3 image_processor.py sample_image_list.csv` if you just want to process and convert them.
* Or run `python3 html_from_csv.py` to create the table

### File format
The `.csv` file must have the following headers for the python scripts to work:


| Organization | Logo URL | Filename |
|--------------|----------|----------|
|              |          |          |


### Notes
- It will automatically make a backup of the image, or image directory first.
- log file contains data about the run
- Cache is there to avoid unnecessary downloading

- Use `--help` for command line arguments.

