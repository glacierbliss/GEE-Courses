#GD_Landsat_04_Animate.py creates an animation of images from a folder. Adds title slide and time stamp text.
#
#See also: GD_TLAN.R, GD_TLAN.py, and test_anim.py 
#
#This code modified from GD_TLAN.py, and borrowing from GD_Lands_03_Select etc.
#
#Linear code structure instead of functions. Not sure if that will
#impact performance or other things, but try it for now.
#
# TODO: construct folders/image list from camera name instead of vice versa
# (easier than trying to get all images into same directory).
#
# TODO: allow cropping on the fly
#
#GENERAL NOTE: PIL.JpegImagePlugin.JpegImageFile is a subclass of Image.Image that is specifically used for JPEG images.

import os
import numpy as np
import statistics
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo #time zones
# import piexif  # To handle EXIF data easily
from pathlib import Path
import time as stopwatch
import pandas as pd
from collections import Counter

##############
#functions
##############
# Function to add the timestamp to the image
def add_timestamp(image, timestamp):
    # Create an ImageDraw object. image=img
    draw = ImageDraw.Draw(image)
    # Choose a font and size (make sure to adjust the font path if necessary)
    try:
        font = ImageFont.truetype(r"D:\U\clutter\NPSlogo\FrutigerLTStd\FrutigerLTStd-Black.otf", 72)  # Default font #was 144
    except IOError:
        font = ImageFont.load_default(72)  # Use default font if Frutiger is not found
    #text position (measured from top left in pixels)
    text_position=(40,60) #60,20
    # Add text to the image
    draw.text(text_position, timestamp, font=font, fill="orange")
    # image.save("example_image.png")
    return image

#have list already...
# #function to list image files
# def list_image_files(root_dir):
#     #simple way inside 1 folder: image_files = [f for f in os.listdir(folder_image) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
#     valid_extensions = ('.jpg', '.jpeg', '.png') #, '.gif', '.bmp', '.tiff', '.heic')
#     image_files = []
# 
#     for dirpath, _, filenames in os.walk(root_dir):
#         for filename in filenames:
#             if filename.lower().endswith(valid_extensions):
#                 full_path = os.path.join(dirpath, filename)
#                 image_files.append(full_path)
# 
#     return image_files

#############
#setup
#############
folder_base = r'C:\Users\andyb\Documents\U\SEAN_Glacier-Dynamics' #os.path.join()
folder_shp = r'C:\Users\andyb\Documents\U\GEE-Courses\data'
file_path=os.path.join(folder_base,'glacierPropsLandsat.csv')

glaciers = pd.read_csv(file_path) #contains Name, LatCenter, LonCenter, two types of bounding boxes (see GD_Landsat_01_Setup).
glaciers['Name']

#choose one glacier
glacier = glaciers.iloc[0] #0=Margerie, 12=McBride
glacierdf=glaciers.iloc[[0]]
print('You chose: ' + glacier['Name'])
folder_out=os.path.join(folder_shp, glacier['Name'])
folder_fig=os.path.join(folder_out, 'Figures')
folder_anim=os.path.join(folder_out, 'Anim')
#create folder_anim if it doesn't exist
if not os.path.exists(folder_anim):
  os.makedirs(folder_anim)

# load metadata from CSV
file_meta = os.path.join(folder_out, 'LandsatMetadata.csv')
mdf = pd.read_csv(file_meta, parse_dates=['DATE_ACQUIRED', 'datetime'])
#file_metaBackup = os.path.join(folder_out, 'LandsatMetadataBackup.csv')
#mdf.to_csv(file_metaBackup, index=False)

print(f"Image info loaded from: {file_meta}") #and backed up to: {file_metaBackup}")
print(mdf.dtypes) #variable datetime has type datetime64[ns]
mdf.iloc[0]
mdf['ImagePath'][0] #image path has the whole path.
#check if there's a keep column, otherwise error
if 'Keep?' not in mdf.columns:
    raise Exception("Metadata does not include Keep column. Run GD_Landsat_03_Select first.")

#construct folder and file names
# folder_image=folder_out
# folder_image=Path(folder_base,year,folder_name)
file_mp4 = Path(folder_anim,'LandsatAnim.mp4')
print(f'Loading from\n{folder_out}\nand saving to\n{file_mp4}.')

# Timing
t_start = stopwatch.time()

#############
#select images for this animation
#############
#mdf['Keep?'] is an index into images and times = True to keep

#OLD:
# match desc: #desc= descriptor or 2 digit text to keep files organized
#   case "all": #keep all
#     indKeep = [True] * len(image_files)
#   # case "0700" HHMM
#   case d if isinstance(d, str) and d.isdigit() and len(d) == 4:
#     print(f"Looks like a string time: {d}")
#     indKeep=[t==d[:2]+':'+d[2:] for t in times_formatted]
# case _:
#   print("Unknown input for description 'desc'.") # indKeep = [True] * len(image_files)

#TODO: consider cases for keeping monthly least-cloudy or annual (e.g. Sept least cloudy)
#SEE: GD_TLAN.py

print(f'Keep times: {sum(mdf['Keep?'])} of {len(mdf)}')

#mdf reduced via Keep flag
mdf=mdf[mdf['Keep?']]
mdf.iloc[0]

#check if sorted (so far, yes)
print(f"mdf is sorted ascending: {mdf['datetime'].is_monotonic_increasing}") # Output: True

##############
#create title slide from first image
##############
# Create a new image
#background colors: park service logo light brown #c18350, green #45583a, darker brown #9d6c43, off white #fdfdfd
#plain background: image = Image.new('RGB', (images[0].size[0], images[0].size[1]), color='#c18350')
# image1=images[0] #or -1 for last image
#get fresh copy of first image for background
image = Image.open(mdf['ImagePath'].iloc[0])
image_w=image.size[0] #not sure why, but image.size[0] doesn't work here - funny interaction effect? they both have same value at the console.
image_h=image.size[1]
gray = Image.new('RGB', (image_w, image_h), color='gray')
# Create a grayscale version
# gray = image.convert("L").convert("RGB")  # Convert to RGB to blend
# Blend original and grayscale (adjust alpha for intensity)
# overlay = Image.blend(image, gray, alpha=0.75)  # 0.0 = original, 1.0 = fully gray
# image=overlay
# Create an ImageDraw object
draw = ImageDraw.Draw(image)
# Define the text and font
text=' \n\n'.join([
  glacier['Name'],
  mdf['datetimestr'].iloc[0]+ ' to '+mdf['datetimestr'].iloc[-1],
  'Landsat images from USGS EROS Data Center',
  'Animation by Andy Bliss, Physical Scientist',
  'Southeast Alaska Network, National Park Service'])
# Optional: Load a font (default font if not specified)
try:
  font = ImageFont.truetype(r"D:\U\clutter\NPSlogo\FrutigerLTStd\FrutigerLTStd-Black.otf", 72) #was 144
except IOError:
  try:
    print('Frutiger font not found, trying Arial bold')
    font = ImageFont.truetype("arialbd.ttf", size=72) #should work, maybe not on linux? #was 144
  except IOError:
    print('Arial not found, using default font')
    font = ImageFont.load_default(72) #was 144

# Draw the text on the image
draw.text((40, 240), text, fill="orange", font=font) #was 80,80 white
# draw.multiline_text((10, 40), text, fill="orange", font=font)

# image.show() gives OSError: [WinError 6] The handle is invalid
#AKB Note: it's trying to save a temporary file then open in png viewer
#this works instead:
# plt.figure(figsize=(12,8))
# plt.imshow(image)
# plt.axis('off')
# plt.show()

# Save the image
image.save(Path(folder_anim,glacier['Name']+'_TitleSlide.png'))

n_images=len(mdf)
n_images
#repeat title slide 15 times so it is readable
image_files=list(mdf['ImagePath']) #kept it in a dataframe long enough, now going to list to match GD_TLAN.py
image_files=[str(Path(folder_anim,glacier['Name']+'_TitleSlide.png'))]*15+image_files
times=list(mdf['datetime'])
times = [times[0]] * 15 + times
len(times)
progress_fraction=[(t-times[0])/(times[-1]-times[0]) for t in times] #should still work, otherwise revert to max/min
len(progress_fraction)

fig1, ax1 = plt.subplots() # Creates a new Figure and Axes object
ax1.plot(times,progress_fraction, color='blue')
ax1.set(xlabel="Date", ylabel="Value",)
fig1.autofmt_xdate()
plt.show()

# Timing
t_load = stopwatch.time()

#############
# Function to create an animation with date/time overlay from EXIF and save as MP4
############
# def create_animation(folder_image, file_mp4):
# Function to update the image in the animation
def update_frame(i): #i=0
    ax.clear()  # Clear the previous frame
    ax.axis('off')  # Keep the axis hidden
    # image_path = Path(folder_image, image_files[i])
    image_path = image_files[i]
    if 'TitleSlide.png' in image_path:
      img = Image.open(image_path)
      ax.imshow(img)  # Show the current image (defaults to aspect='equal')
    else:
      try:
        img = Image.open(image_path)
    
        # #AKB version:
        # time=img._getexif()[36867] #36867 is DateTimeOriginal
        # # timestamp=timestamp.replace(":", "-",2)
        # time_py= datetime.strptime(time, "%Y:%m:%d %H:%M:%S")
        # if flagUTC: #camera recorded in UTC.
        #   time_py = time_py.replace(tzinfo=ZoneInfo("UTC"))
        #   # Convert to Alaska time (AKDT)
        #   time_py = time_py.astimezone(ZoneInfo("Etc/GMT+8"))
        # time_str= time_py.strftime("%Y-%m-%d %H:%M")
        # # Can do multiline text: 
        # # timestamp='McBride \n'+timestamp
    
        img_with_text = add_timestamp(img, times[i].strftime("%Y-%m-%d"))
        # images.append(img_with_text)
  
        ax.imshow(img_with_text)  # Show the current image (defaults to aspect='equal')
        # ax.plot(np.array([0, progress_fraction[i]])*frame_gray.shape[1], np.array([frame_gray.shape[0], frame_gray.shape[0]])-50, color='#2b8cbe',linewidth=3, linestyle='-')
        # ax.plot(np.array([0, progress_fraction[i]])*figw, np.array([figh, figh])-50, color='orange',linewidth=3, linestyle='-') #2b8cbe
        # ax.plot(np.array([0, progress_fraction[i]])*image_w, np.array([image_h,image_h])-50, color='orange',linewidth=3, linestyle='-') #2b8cbe
        ax.plot(np.array([0, progress_fraction[i]])*image_w*.95, np.array([15,15]), color='orange',linewidth=9, linestyle='-')#*.95 so it doesn't overextend #2b8cbe
      except Exception as e:
        print(f'Bad image frame: {image_path}: {e}')
        # images.append(float('nan'))
    
# plt.show() #if plot show is on, resolution of animation is much lower (could be good)

#############
# Create the animation
############
# Create a plot to display the images as an animation
# fig, ax = plt.subplots()
#fig = plt.figure(figsize=(12.0, 12.0 * frame_gray.shape[0] / frame_gray.shape[1]), facecolor='g') #was 'w'
# Create a figure with the same dimensions as the image
# figw=image.size[0]/100/3 #/100 account for dpi, /3 reduce size by factor
# figh=image.size[1]/100/3
figw=image.size[0]/100 #/100 account for dpi, /3 reduce size by factor
figh=image.size[1]/100
fig = plt.figure(figsize=(figw,figh), dpi=100)  # Adjust dpi as needed
# Add an axes to the figure
ax = fig.add_axes([0, 0, 1, 1])  # Full size
ax.axis('off')  # Hide the axis
#AKB verified that this results in proper aspect ratio.

# nimages=len(images)
nimages=len(times)
nimages=30 #testing
fps=15
duration=nimages/fps
# Create the animation (shell)
ani = animation.FuncAnimation(fig, update_frame, frames=nimages, interval=duration, repeat=True)
# Save the animation as an MP4 video using ffmpeg
ani.save(file_mp4, writer='ffmpeg', fps=fps)

print(f"Animation saved as {file_mp4}")

#2025-12-2 MovieWriter ffmpeg unavailable; using Pillow instead.
#Then I got a ValueError: unknown file extension: .mp4
#trying with Pillow
file_gif= file_mp4.with_suffix(".gif")
ani.save(
    file_gif,
    #Grok example code not quite analogous
    #save_all=True,
    #append_images=ani[1:],
    #duration=66.666,      #80 gives ~12.5 fps = 1/80*1000. # milliseconds between frames (100 = 10 fps)
    #loop=0,
    #optimize=True     # Reduces file size
    fps=fps
)

# Timing
# for i in range(1000000):
#     pass
t_end = stopwatch.time()
print(f"n={n_images}. Timing (sec): exif: {t_exif-t_start:.2f}, load: {t_load-t_exif:.2f}, anim: {t_end - t_load:.2f}, total elapsed: {t_end - t_start:.2f}.")

#############
#Notes
#############
# 20250818_McBride_1_Terminus_Wing_all.mp4
# n=2399. Timing (sec): exif: 18.82, load: 6.18, anim: 3767.98, total elapsed: 3792.99.
