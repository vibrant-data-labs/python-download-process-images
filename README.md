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

## Setup
Copy the sample config to your own. This file will not be committed.
```
cp config.sample.ini config.ini
```
Then edit the config, filling in your own values.

## Usage as a module
```python
import imagetools

imagetools.download_images(csv_file="sample_image_list_noextention.csv")
imagetools.process_images(resize=True,width=200,height=200,
                          grayscale=True,padding=False,
                          padding_width=100,padding_height=100)
imagetools.upload_images(s3_bucket="this-bucket")
```
### CSV format
The `.csv` file must have the following positional column values for the python scripts to work  (the header names do not matter):

| name | image_url | filename |
|------|-----------|----------|
|      |           |          |

### Notes
- Cache is there to avoid unnecessary downloading

