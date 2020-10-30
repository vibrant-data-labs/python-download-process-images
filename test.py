import imagetools

imagetools.download_images(csv_file="sample_image_list_noextention.csv")
    # TODO: add parameter as_png=True to convert all images to png when downloaded

# for each file in foldername - process images
    # option to - resize, convert to greyscale, add padding, add background color
    # def process_images (resize_h=200, resize_w=200, add_padding = 0, to_grey=False):
    
imagetools.upload_dir_to_s3("downloaded_images")
