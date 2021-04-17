import pandas as pd
import imagetools

df = pd.read_csv('data/test_df.csv')
image_directory = "data/images"
newdata = imagetools.download_images_df(df, image_dir=image_directory, as_png=True) # convert all to png if possible
newdata.to_csv('results/test_df_results.csv')