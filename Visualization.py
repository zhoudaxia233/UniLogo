import ast
import pandas as pd
from pathlib import Path
from PIL import Image


size=100
datapath = Path.cwd() / Path("images") / 'imgs0617'

def string_to_list(input_str):
    try:
        return ast.literal_eval(input_str)
    except ValueError:
        print("The input string is not a valid list")

rank_df = pd.read_excel('uni ranking xy 0617.xlsx')
rank_df['HSV'] = rank_df['HSV'].apply(string_to_list)
rank_df['main_color'] = rank_df['main_color'].apply(string_to_list)

def x(hs, size=9):
    x = round(hs[0]*size)
    return x

def y(hs, size=9):
    y = round(hs[1]*size)
    return y

rank_df['X'] = rank_df['HSV'].apply(x,size = size-1)
rank_df['Y'] = rank_df['HSV'].apply(y,size = size-1)

rank_df.to_excel(f'uni ranking xy 0617 {size}.xlsx',index=False)

draw_df = rank_df.loc[rank_df.groupby(['X','Y'])['ranking'].idxmin()]

def replace_transparent_with_white(image_path):
    # Open the image file
    img = Image.open(image_path)

    # Make sure the image has an alpha (transparency) channel
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):

        # Convert the image into RGBA if it is not already
        alpha = img.convert('RGBA')

        # Create a new image ('RGB') and paste the RGBA image into it
        # A white (255, 255, 255) background is created for this new image
        bg = Image.new('RGB', alpha.size, (255, 255, 255))
        bg.paste(alpha, mask=alpha.split()[3])  # 3 is the alpha channel in an RGBA image

        return bg

    else:
        return img


def paste_image_on_grid(image_size, grid_size, paste_image_path, row, col, img=None):
    # 计算每个子图的大小
    sub_size = (image_size[0]//grid_size, image_size[1]//grid_size)

    # 创建一张空白图片
    if img is None:
        img = Image.new('RGB', image_size, (255, 255, 255))

    # 打开你希望粘贴的图片并将其缩放到子图大小
    paste_img = replace_transparent_with_white(paste_image_path)
    paste_img = paste_img.resize(sub_size, Image.ANTIALIAS)

    # 在指定位置粘贴图片
    img.paste(paste_img, (col*sub_size[0], row*sub_size[1]))

    # 显示图片
    # img.show()

    return img


image_size = (5000, 5000)
grid_size = size
t=1

for index, row in draw_df.iterrows():
    paste_image_path = datapath / (row['univNameEn']+'.png')
    if t==1:
        img = paste_image_on_grid(image_size, grid_size, paste_image_path, row['X'], row['Y'])
        t=0
    else:
        img = paste_image_on_grid(image_size, grid_size, paste_image_path, row['X'], row['Y'], img=img)

img.save(f"{size}.png")