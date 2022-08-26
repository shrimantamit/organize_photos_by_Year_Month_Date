# organize_photos_by_Year_Month_Date
 
This script organizes images and videos into subfolders based on the  image's or video's creation time.
While re-organizing the files it deleted following files from the directories: 'Thumbs.db', '.DS_Store', 'ZbThumbnail.info', '.THM'

Many times, image's metadata is missing or not correct. So file creation date is determined as follows:
1. Get FileName, and check if its name starts with YYYYMMDD
2. Else, try fetching exif data
3. If that fails too, fetch file birthdate (MacOS) This is kept as last option because if files are moved around using drives or downloaded from google photos etc, this could be quite incorrect.

For Video files, I tried using hachoir, but for MOV files, it was always giving me incorrect creation date. It was off by 7+ months in past.
Finder app and CLI was showing correct information but hachoir was unable to fetch that infrmation.
You can see commented code.

For videos, 
1. Get FileName, and check if its name starts with YYYYMMDD
2. If that fails too, fetch file birthdate (MacOS).

Based on returned date, folder structure like below is created and files are moved in respective folders.
if same file already exists, move file as renamed file name. e.g: 'Original_file_name_rename_2012_11_10_9_8_7.jpg'
```
E.g.:
xxx@yyyy tmp % cat tree.txt 
images_reorg_dst
└── 2020
    ├── 2020_01
    │        └── 2020_01_29
    │            └── 2020_January_29_20_42_25_3240.JPG
    ├── 2020_10
    │        └── 2020_10_30
    │            └── 2020_October_30_18_41_43_4628.JPG
    ├── 2020_11
    │        └── 2020_11_29
    │            └── 2020_November_29_12_48_36_4887.MOV
    └── 2020_12
        ├── 2020_12_01
        │        └── 2020_December_01_21_44_40_4909.MOV
        └── 2020_12_30
            └── 2020_December_30_23_55_45.MOV
```
At the end, empty directories from source folder are deleted.
