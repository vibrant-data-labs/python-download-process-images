# Python Download and Processing Image Module
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
sudo apt install libcanberra-gtk-module python3-pip python3 imagemagick inkscape webp -y
python3 -m pip install -r requirements.txt
```

## Usage as a module
```
import imagetools

imagetools.download_images("sample_image_list.csv")
imagetools.upload_dir_to_s3("downloaded_images")
```
### CSV format
The `.csv` file must have the following positional column values for the python scripts to work  (the header names do not matter):

| name | image_url | filename |
|------|-----------|----------|
|      |           |          |

### Notes
- Cache is there to avoid unnecessary downloading

