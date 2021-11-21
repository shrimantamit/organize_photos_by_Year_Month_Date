"""
Author: Amit Karve
Date: Nov 19 2021

V1: Initial file
V2: Changes made to accomodate .xmp and AAE metadata files
    For xmp files, edit history is lost, but settings like, temp, tint, exposure etc is maintained.
    Not yet verified for AAE file.
"""

from genericpath import exists
from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
from datetime import datetime
import os
import shutil
import fnmatch

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
        
# Reversing the Tags
reversed_TAGS = dict(((v, k) for k, v in TAGS.items()))

# define what image and video types to search for
image_types = ('.png', '.jpeg', '.jpg', '.gif', '.bmp', '.HEIC')
video_types = ('.mov', '.mp4', '.avi', '.mpg')
files_to_delete = ('Thumbs.db', '.DS_Store', 'ZbThumbnail.info', '.THM')
metadata_types = ('.xmp', '.AAE')

###############
def get_file_exif_properties(src_file_loc):
    """
    fetch and return file creation date.
    if selected file is not of given time, return None.
    """
    # Considering metadata files, changing data type to list
    current_file = []
    current_file.append(Path(src_file_loc))
    # return if file does not exist
    if current_file[0].is_file() is False:
        return

    # Added upper to make file extention find case-insensative
    if current_file[0].suffix.upper() in map(str.upper, image_types):
        try:
            # Try to open the image file
            image = Image.open(current_file[0])
            # extract EXIF data
            exifdata = image.getexif()
            DateTimeOriginal = exifdata[reversed_TAGS["DateTimeOriginal"]]
            DateTimeOriginal_obj = datetime.strptime(DateTimeOriginal, '%Y:%m:%d %H:%M:%S')
        except:
            # Check file_name has YYYYMMDD format
            # e.g.: 20121230_174101000_iOS.*
            # came across file name like '17850413683_fc24949cbe_o.jpg'
            # So moved the date fetching logic up and down and added year check to make some sense.
            # Note: Year 2000 is chosen randomly
            print(f"CURRENT FILE: {current_file[0]}")
            DateTimeOriginal_obj = get_date_by_file_name(current_file[0])
            if DateTimeOriginal_obj and (DateTimeOriginal_obj.year < 2000):
               DateTimeOriginal_obj = None
            
            # fetching birthtime
            if DateTimeOriginal_obj is None:
                stats = os.stat(str(current_file[0]))
                DateTimeOriginal_obj = datetime.fromtimestamp(stats.st_birthtime)
        
    elif current_file[0].suffix.upper() in map(str.upper, video_types):
        # Tried to use Hachoir, but it always resulted in wrong date 
        # print("need to use Hachoir")
        # parser = createParser(str(current_file))
        # metadata = extractMetadata(parser)
        # metadata_dict = metadata.exportDictionary()
        # DateTimeOriginal = metadata_dict['Metadata']['Creation date']
        # DateTimeOriginal_obj = datetime.strptime(DateTimeOriginal, '%Y-%m-%d %H:%M:%S')
        DateTimeOriginal_obj = get_date_by_file_name(current_file[0])
        if DateTimeOriginal_obj is None:
            stats = os.stat(str(current_file[0]))
            DateTimeOriginal_obj = datetime.fromtimestamp(stats.st_birthtime)

    else:
        print(f'''Given file "{src_file_loc}" is not image or video.''')
        if current_file[0].name in files_to_delete or current_file[0].suffix.upper() in map(str.upper, files_to_delete):
            print(f'''But current file is of any if these types: {files_to_delete},
            so it will be deleted now.''')
            print(f"deleting {current_file[0]}")
            os.remove(str(current_file[0]))
            try_deleting_dir(current_file[0].parent)
        return

    # Check if metadata file for image file exists.
    #  if yes, get that file information and append to current_file list
    metadata_file_list = fnmatch.filter(os.listdir(current_file[0].parent), current_file[0].stem+'*')
    # If length is more than 1 that mean MD file exists, so removing original image file entry
    if len(metadata_file_list) > 1:
        metadata_file_list.remove(current_file[0].name)
        # Assuming that we have more than 1 MD file,
        # converting each MD file into Path Object and apending it to current_path list
        for each_MD_file in metadata_file_list:
            # Path(src_file_loc)
            print(os.path.join(current_file[0].parent, each_MD_file))
            current_file.append(Path(os.path.join(current_file[0].parent, each_MD_file)))

    return current_file, DateTimeOriginal_obj


def try_deleting_dir(file_parent):
    '''
    Try to delete given directory.
    If files exist in directory, its no op.
    '''
    try:
        if len(os.listdir(file_parent)) == 0:
            os.rmdir(file_parent)
    except:
        pass


def create_dir_mv_file(current_file_DateTimeOriginal_obj):
    # from current_file_hash separate current_file and DateTimeOriginal_obj
    print(current_file_DateTimeOriginal_obj)
    current_file_list, DateTimeOriginal_obj = current_file_DateTimeOriginal_obj
    year_folder_name = str(DateTimeOriginal_obj.year)
    # {:02d} will make month and dates in 2 digits. E.g.: 01, 02, etc
    month_folder_name = '{:02d}'.format(DateTimeOriginal_obj.month)
    two_digit_date = '{:02d}'.format(DateTimeOriginal_obj.day)
    file_dest_folder = year_folder_name + '_' + month_folder_name + '_' + two_digit_date
    final_dest_path = os.path.join(dst_dir, year_folder_name,
        (year_folder_name + '_' + month_folder_name), file_dest_folder)

    if not os.path.isdir(os.path.abspath(final_dest_path)):
        print("Path did not exist, creating the directory")
        os.makedirs(os.path.abspath(final_dest_path))
        print(f"Path now created : {final_dest_path}")

    # now as path is created, move file from source to destination.
    # But first check if same name exists, if yes, move as renamed file.
    date_time_new_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    for current_file in current_file_list:
        new_file_location = Path(os.path.join(final_dest_path, current_file.name))
        if new_file_location.is_file() == False:
            shutil.move(current_file, new_file_location)
            print(f"File moved to new location: {new_file_location}")
        else:
            new_name = new_file_location.stem +'_rename_'+ date_time_new_name + new_file_location.suffix
            new_renamed_path = os.path.join(new_file_location.parent, new_name)
            # shutil.copy2(current_file, os.path.join(new_file_location.parent, new_name))
            shutil.move(current_file, new_renamed_path)
            print(f"File moved to new location: {new_renamed_path}")
    
        # Try to delete empty directory:
        try_deleting_dir(current_file.parent)
    

def absoluteFilePaths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def get_date_by_file_name(current_file):
    # Check file_name has YYYYMMDD format
    # e.g.: 20121230_174101000_iOS.*
    file_YYYYMMDD = (current_file.stem)[:8]
    if file_YYYYMMDD.isdecimal() is False:
        return
    try:
        DateTimeOriginal_obj = datetime.strptime(file_YYYYMMDD, '%Y%m%d')
        return DateTimeOriginal_obj
    except:
        return


def removeEmptyFolders(path, removeRoot=True):
    '''Function to remove empty folders.
    Ref: https://gist.github.com/jacobtomlinson/9031697'''
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        print(f"Removing empty folder: {path}")
        os.rmdir(path)
    
###############

src_dir = '/Volumes/XXX/Photos/Miscellaneous/YYY_photos'
dst_dir = '/Volumes/XXX/Photos/Miscellaneous/YYY_photos_sorted'

for each_file in absoluteFilePaths(src_dir):
    print(each_file)

    current_file_DateTimeOriginal_obj = get_file_exif_properties(each_file)
    if current_file_DateTimeOriginal_obj is not None and len(current_file_DateTimeOriginal_obj) == 2:
        create_dir_mv_file(current_file_DateTimeOriginal_obj)


removeEmptyFolders(src_dir)

