Hip-Label-Tool
===============

A tool for labeling etiology and grade of a hip, implemented with Python Tkinter.

Directory information
-----------------
```
hip_label_tool  
|  
├──label.py   
|  
├──DrLiao
|    ├──HumanOA_Annotation_masterTable_0225_2020.xls
|    ├──original
|    ├──crop
|    └──DrLiao_labels (automatically generated after labeling)
|
├──DrLiao_export.csv  (automatically generated after labeling)
|     
├──README.md
|
├──installation.md 
|
└──src
```

Environment
----------
Please refer to installation.md


Setting
-----
1. ### **Data and directory:**
   * Make sure you have the same structure as above-mentioned directory.
   * If you are `DrX`, for example, rather than `DrLiao`. Please have:
        1. Change `DrLiao` folder name into `DrX`.
        2. Find all `DrLiao` in `label.py` and replace every of them with `DrX`. You should change **7** places.

2. Run
    ```console
    foo@bar:~$ python3 label.py
    ```
    then you can have the following GUI.
    ![image info](./src/tutorial.png)

3. Adjust display resolution until you have the full view of the GUI.
    ![image info](./src/resolution.png)
    or check this out: https://support.apple.com/en-us/HT202471

Usage
-----
1. Run
    ```console
    foo@bar:~$ python3 label.py
    ```
2. Click `Image Folder` button and choose `DrLiao`folder.

3. Start labeling and feel free to leave the GUI anytime.


Original  project address: [BBox-Label-Tool](https://github.com/puzzledqs/BBox-Label-Tool)



