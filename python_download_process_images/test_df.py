import pandas as pd
import python_download_process_images.imagetools as imagetools

df = pd.read_csv('./data/image_urls_for_jesse.csv')
image_directory = "./data/images"
newdata, errors = imagetools.download_images_df(df, image_dir=image_directory, as_png=True) # convert all to png if possible
newdata.to_csv('results/image_urls_for_jesse_output.csv')
errors.to_csv('results/image_urls_for_jesse_errors.csv')
# imagetools.process_images(image_dir='data/images', resize=True, width=200, height=200,
#              grayscale=True, padding=False,
#              padding_width=100, padding_height=100)