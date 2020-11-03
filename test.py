import imagetools

# padding dimensions set image to that width and height and fill in empty space with dominant color padding

# def download_images(csv_file="sample_image_list.csv",as_png=True,no_header=False):
imagetools.download_images(csv_file="sample_image_list_noextention.csv")

# def process_images(image_dir=IMAGE_DIR,change_type=None,resize=False,width=200,height=200,grayscale=False,padding=False,padding_width=0,padding_height=0,background_color=None):
imagetools.process_images(resize=True,width=200,height=200,
                          grayscale=True,padding=False,
                          padding_width=100,padding_height=100)
# def upload_images(image_dir=IMAGE_DIR,s3_bucket=BUCKET)
imagetools.upload_images()