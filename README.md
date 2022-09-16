# Python Download and Processing Image Module
## Initial Setup
### macOS
1. Install [Homebrew](https://brew.sh/)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
2. Install python 3 via brew
```bash
brew install python3
```
If necessary, run `brew link` to symlink Python 3 to the main `python3` command: 
```bash
brew link python@3.9 # or whatever version
```
3. Install [pip](https://pypi.org/project/pip/) for python

```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```
Or do it with brew:
```bash
brew postinstall python3
```
> You can make sure which version you are on by running `python3 --version`

4. Install `pip` prerequisites
```bash
## Dependencies
brew install python3 cairo imagemagick webp
python3 -m pip install -r requirements.txt
```
> Please note that if you are using Anaconda for development, you must also install the cairo package via conda:
```bash
conda install cairo
```
### Ubuntu
```
sudo apt install libcanberra-gtk-module python3-pip python3 imagemagick inkscape webp -y
python3 -m pip install -r requirements.txt
```
## Project Setup
1. Download or clone this repository: 
```
git clone https://github.com/ericberlow/python-download-process-images.git
```
2. Change to this project's directory in your terminal: 
```
cd python-download-process-images
```
3. Copy the sample config to your own. This file will not be committed.
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

