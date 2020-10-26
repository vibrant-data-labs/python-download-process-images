# Python Download and Processing Image Scripts
1. Download or clone this repository: 
```
git clone https://github.com/ericberlow/python-download-process-images.git
```
2. Change to this project's directory in your terminal: 
```
cd python-download-process-images
```

## Dependencies
> macOS
```
brew install python imagemagick inkscape webp
python3 -m pip install -r requirements.txt
```
> Ubuntu
```
sudo apt-get install libcanberra-gtk-module python3-pip python3 imagemagick inkscape webp -y
python3 -m pip install -r requirements.txt
```

## Usage
```
python3 image_downloader.py sample_image_list.csv
python3 image_processor.py downloaded_images --greyscale --resize --width 200 --height 200
python3 html_from_csv.py
```
### CSV format
The `.csv` file must have the following positional column values for the python scripts to work  (the header names do not matter):

| Organization | Logo URL | Filename |
|--------------|----------|----------|
|              |          |          |

### Notes
- It will automatically make a backup of the image, or image directory first.
- log file contains data about the run
- Cache is there to avoid unnecessary downloading
- Use `--help` for command line arguments.

