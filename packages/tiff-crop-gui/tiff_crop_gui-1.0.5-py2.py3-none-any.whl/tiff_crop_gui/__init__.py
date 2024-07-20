#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tiff_gui.py: Automatically crops a directory of tiff images."""

__author__ = "Hudson Liu"
__email__ = "hudsonliu0@gmail.com"

import glob
import os

from tqdm import tqdm
from PIL import Image
import dearpygui.dearpygui as dpg
import numpy as np

# Banner
A = """
████████╗██╗███████╗███████╗     ██████╗██████╗  ██████╗ ██████╗ 
╚══██╔══╝██║██╔════╝██╔════╝    ██╔════╝██╔══██╗██╔═══██╗██╔══██╗
   ██║   ██║█████╗  █████╗█████╗██║     ██████╔╝██║   ██║██████╔╝
   ██║   ██║██╔══╝  ██╔══╝╚════╝██║     ██╔══██╗██║   ██║██╔═══╝ 
   ██║   ██║██║     ██║         ╚██████╗██║  ██║╚██████╔╝██║     
   ╚═╝   ╚═╝╚═╝     ╚═╝          ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     
"""

def main():
    print(A)
    # Get path
    coords = []
    while True:
        dir_ = input("Enter the directory/path containing your TIFF images: ")
        try:
            os.chdir(dir_)
            break
        except:
            print("That directory is not valid.")
    dir_ = dir_ + "/" if dir_[-1] != "/" else dir_ # remove diagonal if it exists

    # Ensure that the path abides by necessary formatting
    print(f"Using directory \"{dir_}\"")

    # Pick the specific image
    while True:
        imgname= input("Enter the name of the .tif image you'd like to use to crop: ")
        try:
            image = Image.open(f"{dir_}{imgname}")
            break
        except:
            print("That image name is not valid.")

    dpg.create_context()

    image = image.resize((image.width // 2, image.height // 2), Image.Resampling.LANCZOS)
    image = image.convert("RGBA")
    dpg_img = np.array(image).astype(np.float32) / 255.0
    dpg_img = dpg_img.flatten()

    # Update Rectangle Pos.
    def update_rect_w(sender):
        sv = dpg.get_value(sender)
        dpg.configure_item("X", max_value = image.width - sv)
        dpg.configure_item(2, pmax = (sv  + dpg.get_value("X"), dpg.get_value("H") + dpg.get_value("Y")))
    def update_rect_h(sender):
        sv = dpg.get_value(sender)
        dpg.configure_item("Y", max_value = image.height - sv)
        dpg.configure_item(2, pmax = (dpg.get_value("W") + dpg.get_value("X"), dpg.get_value("Y") + sv))
    def update_rect_x(sender):
        sv = dpg.get_value(sender)
        dpg.configure_item("W", max_value = image.width - sv)
        dpg.configure_item(2, pmin = (sv, dpg.get_value("Y")), pmax = (dpg.get_value("W") + dpg.get_value("X"), dpg.get_value("Y") + dpg.get_value("H")))
    def update_rect_y(sender):
        sv = dpg.get_value(sender)
        dpg.configure_item("H", max_value = image.height - sv)
        dpg.configure_item(2, pmin = (dpg.get_value("X"), sv), pmax = (dpg.get_value("W") + dpg.get_value("X"), dpg.get_value("Y") + dpg.get_value("H")))
    def on_click(sender):
        coords.append([int(dpg.get_value("X")), int(dpg.get_value("Y")), int(dpg.get_value("W")), int(dpg.get_value("H"))])
        dpg.stop_dearpygui()

    # Registries
    with dpg.texture_registry():
        dpg.add_static_texture(image.width, image.height, dpg_img, tag="imagetoedit")

    # File Selector
    with dpg.file_dialog(directory_selector=False, show=False, id="file_dialog_id", width=500 ,height=200):
        dpg.add_file_extension(".tif", color=(0, 255, 0, 255), custom_text="[TIFF Image Files]")

    # Windows
    WIDTHCONST = 450
    with dpg.window(
            label = "Position",
            no_collapse = True,
            no_move = True,
            no_close = True,
            no_resize = True,
            min_size = (WIDTHCONST, image.height // 2),
            max_size = (WIDTHCONST, image.height // 2),
            pos = (0, 0)
        ):
        dpg.add_slider_float(label="X Pos.", tag = "X", default_value=image.width // 4, max_value=image.width // 2, callback = update_rect_x, width = 350)
        dpg.add_slider_float(label="Y Pos.", tag = "Y", default_value=image.height // 4, max_value=image.height // 2, callback = update_rect_y, width = 350)

    with dpg.window(
            label = "Size",
            no_collapse = True,
            no_move = True,
            no_close = True,
            no_resize = True,
            min_size = (WIDTHCONST, image.height // 2),
            max_size = (WIDTHCONST, image.height // 2),
            pos = (0, image.height // 2)
        ):
        dpg.add_slider_float(label="Width", tag = "W", default_value=image.width // 2, max_value=0.75 * image.width, callback = update_rect_w, width = 350)
        dpg.add_slider_float(label="Height", tag = "H", default_value=image.height // 2, max_value=0.75 * image.height, callback = update_rect_h, width = 350)

    with dpg.window(
            no_title_bar = True,
            no_collapse = True,
            no_move = True,
            no_close = True,
            no_resize = True,
            min_size = (WIDTHCONST, 40),
            max_size = (WIDTHCONST, 40),
            pos = (0, image.height)
        ):
        dpg.add_button(label = "Crop Image", width = WIDTHCONST - 20, callback = on_click)

    with dpg.window(
            label = "Crop Image Viewer",
            no_collapse = True,
            no_move = True,
            no_close = True,
            no_resize = True,
            min_size = (image.width, image.height + 40),
            max_size = (image.width, image.height + 40),
            pos = (WIDTHCONST, 0)
        ):
        with dpg.drawlist(image.width, image.height):  # or you could use dpg.add_drawlist and set parents manually
                dpg.draw_image("imagetoedit", pmin=(0,0), pmax=(image.width,image.height))
                dpg.draw_rectangle(pmin=(image.width // 4, image.height // 4), pmax=(0.75 * image.width, 0.75 * image.height), tag=2, color = [255, 0, 0])

    dpg.create_viewport(title = "TIFF Cropper -- Hudson Liu", width = image.width + WIDTHCONST + 15, height = image.height + 80)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    # Make cropped images folder
    dir_name = f"Cropped_Images{' (' + str(a) + ')' if (a := len(glob.glob('Cropped_Images*'))) > 0 else ''}" #TODO this doesnt work if, say, "Cropped_images (2)" got deleted
    print(f"Making new directory \"{dir_name}\"... ", end='')
    os.mkdir(dir_name)
    print("Done")

    # Crop 
    c = [2 * i for i in coords[0]]
    for f in glob.glob("*.tif"):
        im = np.array(Image.open(f))
        if abs(im.shape[0] - image.height * 2) >= 10 or abs(im.shape[1] - image.width * 2) >= 10:
            print(f"Skipping over {f} as it is not of the same resolution.")
            continue
        new = im[c[1]:(c[1]+c[3]), c[0]:(c[0]+c[2])]
        i = Image.fromarray(new)
        i.save(f"{dir_name}/{f}")

main()