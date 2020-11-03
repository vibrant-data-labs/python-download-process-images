import imagetools

imagetools.download_images(csv_file="sample_image_list_noextention.csv")

imagetools.process_images(resize=True,width=200,height=200,grayscale=True,padding=True,padding_width=100,padding_height=100)
# for each file in foldername - process images
    # option to - resize, convert to greyscale, add padding, add background color
    # def process_images (resize_h=200, resize_w=200, add_padding = 0, to_grey=False):
    
# imagetools.upload_images()
