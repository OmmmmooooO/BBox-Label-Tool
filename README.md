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
└──installation.md 
```

Environment
----------
Please refer to installation.md


Usage
-----
0. ### **Data and directory :**
   * Make sure you have the same structure as above-mentioned directory.
   * If you are `DrX`, for example, rather than `DrLiao`. Please have:
        1. Change `DrLiao` folder name into `DrX`.
        2. Find all `DrLiao` in label.py and replace every of them with `DrX`. You should change 5 places.

1. Run
    ```console
    foo@bar:~$ python3 label.py
    ```
2. 

Original  project address: [BBox-Label-Tool](https://github.com/puzzledqs/BBox-Label-Tool)



