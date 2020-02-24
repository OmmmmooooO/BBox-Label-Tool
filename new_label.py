from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import Toplevel
from PIL import Image, ImageTk
import datetime
import os
import glob
import json
import random
import platform
import pandas as pd

# image sizes for the examples
SIZE = 256, 256
# panel size for init
PSIZE = 500

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)
        self.area = 0
        self.loadLabelOnly = 0

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.outDir = ''
        self.count = 0
        self.cur = 0
        self.total = 0
        self.undone = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.cla_can_temp = []


        # reference to image and bbox info, "info" set default value
        self.imgInfo = []
        self.infoClass = 'Hip'
        self.infoAge = '0-6 month'
        self.classList = []
        self.ageList = []

        # ----------------- GUI stuff ---------------------
        # >>>>>>> [UPPER PART] <<<<<<<
        # button: Load Unlabel Images
        # button: Load Labeled Images
        self.srcDirBtn = Button(self.frame, text = "Image Folder", command = self.selectSrcDir, width = 10)
        self.srcDirBtn.grid(row = 0, column = 0, sticky = E)
        self.svSourcePath = StringVar()
        self.svSourcePath.set(os.getcwd())
        self.entrySrcDir = Entry(self.frame, textvariable = self.svSourcePath)
        self.entrySrcDir.grid(row = 0, column = 1, columnspan=4, sticky = W+E)
        
        '''
        self.srcLoadBtn = Button(self.frame, text = "Labeled", command = self.selectLoadDir, width = 10)
        self.srcLoadBtn.grid(row = 1, column = 0)
        self.svLoadPath = StringVar()
        self.svLoadPath.set(os.getcwd())
        self.entryLoadDir = Entry(self.frame, textvariable = self.svLoadPath)
        self.entryLoadDir.grid(row = 1, column = 1, columnspan=4, sticky = W+E)
        '''

        # >>>>>>> [CENTER PART] <<<<<<<
        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor = 'tcross')
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, columnspan = 4, sticky = W+E+N+S)

        # >>>>>>> [RIGHT PART] <<<<<<<
        # right side of GUI, left side of patient in x-ray

        # canvas for matched image
        self.matchimgPanel = Canvas(self.frame, cursor = 'tcross')
        self.matchimgPanel.grid(row = 1, column = 5, rowspan = 2, columnspan = 2, sticky = W+E+N+S)
        self.matchID = 'MatchID:'
        self.matchIDLb = Label(self.frame, text=self.matchID)
        self.matchIDLb.grid(row = 3, column = 5, sticky = NW)
        self.matchIDLb.config(font=("Courier", 16))

        self.BtnPanel_L = Frame(self.frame)
        self.BtnPanel_L.grid(row = 4, column = 5, rowspan = 4, sticky = NW)
        self.sideLb_L = Label(self.BtnPanel_L, text = 'Left')
        self.sideLb_L.pack(anchor=NW)
        self.sideLb_L.config(font=("Courier", 20))

        # radio button: Etiology
        self.etiologyLb_L = Label(self.BtnPanel_L, text = 'Etiology:')
        self.etiologyLb_L.pack(anchor=NW)
        self.etiology_L = StringVar()
        self.etiology_L.set(None)
        self.etiologyBtn_L_1 = Radiobutton(self.BtnPanel_L, text='Osteonecrosis', variable=self.etiology_L, value='0', command = self.setEtiology_L, state = DISABLED)
        self.etiologyBtn_L_1.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_2 = Radiobutton(self.BtnPanel_L, text='Avascular necrosis', variable=self.etiology_L, value='1', command = self.setEtiology_L, state = DISABLED)
        self.etiologyBtn_L_2.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_3 = Radiobutton(self.BtnPanel_L, text='Osteoarthritis', variable=self.etiology_L, value='2', command = self.setEtiology_L, state = DISABLED)
        self.etiologyBtn_L_3.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_4 = Radiobutton(self.BtnPanel_L, text='Femoroacetabular impingement', variable=self.etiology_L, value='3', command = self.setEtiology_L, state = DISABLED)
        self.etiologyBtn_L_4.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_5 = Radiobutton(self.BtnPanel_L, text='others', variable=self.etiology_L, value='4', command = self.setEtiology_L, state = DISABLED)
        self.etiologyBtn_L_5.pack(padx=10, pady=4, anchor=NW)

        # radio button: Grade
        self.gradeLb_L = Label(self.BtnPanel_L, text = 'Grade:')
        self.gradeLb_L.pack(anchor=NW)
        self.grades_L = StringVar()
        self.grades_L.set(None)
        self.gradeBtn_L_1 = Radiobutton(self.BtnPanel_L, text='1', variable=self.grades_L, value='0', command = self.setGrade_L, state = DISABLED)
        self.gradeBtn_L_1.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_2 = Radiobutton(self.BtnPanel_L, text='2', variable=self.grades_L, value='1', command = self.setGrade_L, state = DISABLED)
        self.gradeBtn_L_2.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_3 = Radiobutton(self.BtnPanel_L, text='3', variable=self.grades_L, value='2', command = self.setGrade_L, state = DISABLED)
        self.gradeBtn_L_3.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_4 = Radiobutton(self.BtnPanel_L, text='4', variable=self.grades_L, value='3', command = self.setGrade_L, state = DISABLED)
        self.gradeBtn_L_4.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_5 = Radiobutton(self.BtnPanel_L, text='5', variable=self.grades_L, value='4', command = self.setGrade_L, state = DISABLED)
        self.gradeBtn_L_5.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_6 = Radiobutton(self.BtnPanel_L, text='Not specified', variable=self.grades_L, value='5', command = self.setGrade_L, state = DISABLED)
        self.gradeBtn_L_6.pack(padx=10, pady=4, anchor=NW)

        # canvas for cropped image
        self.subPanel_L = Canvas(self.frame, cursor = 'tcross')
        self.subPanel_L.grid(row = 5, column = 3, rowspan = 2, columnspan = 2, sticky = W)

        # bounding boxes parts
        self.btnClear = Button(self.BtnPanel_L, text = 'Clear All', width = 20, height = 2, command = self.reRadioBtn, state = DISABLED)
        self.btnClear.pack()
        self.doneBtn = Button(self.BtnPanel_L, text = 'Save annotation', width = 20, height = 5, command = self.confirmPhoto, fg='red', state = DISABLED)
        self.doneBtn.pack()


        # >>>>>>> [LEFT PART] <<<<<<<
        # left side of GUI, right side of patient in x-ray
        self.BtnPanel_R = Frame(self.frame)
        self.BtnPanel_R.grid(row = 4, column = 0, rowspan = 4, sticky = E+N)

        # annotator
        '''
        self.annotatorLb = Label(self.BtnPanel_R, text = 'Annotator:')
        self.annotatorLb.pack(anchor=NW)
        self.annotatorName = StringVar(self.BtnPanel_R)
        self.annotatorName.set("Name") # default size 100*100
        vcmd = (self.BtnPanel_R.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.annotatorEtr = Entry(self.BtnPanel_R, validate = 'key', validatecommand = vcmd, textvariable=self.annotatorName)
        self.annotatorEtr.pack(anchor=NW)
        '''
        self.sideLb_R = Label(self.BtnPanel_R, text = 'Right')
        self.sideLb_R.pack(anchor=NW)
        self.sideLb_R.config(font=("Courier", 20))

        # radio button: Etiology
        self.etiologyLb_R = Label(self.BtnPanel_R, text = 'Etiology:')
        self.etiologyLb_R.pack(anchor=NW)
        self.etiology_R = StringVar()
        self.etiology_R.set(None)
        self.etiologyBtn_R_1 = Radiobutton(self.BtnPanel_R, text='Osteonecrosis', variable=self.etiology_R, value='0', command = self.setEtiology_R, state = DISABLED)
        self.etiologyBtn_R_1.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_2 = Radiobutton(self.BtnPanel_R, text='Avascular necrosis', variable=self.etiology_R, value='1', command = self.setEtiology_R, state = DISABLED)
        self.etiologyBtn_R_2.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_3 = Radiobutton(self.BtnPanel_R, text='Osteoarthritis', variable=self.etiology_R, value='2', command = self.setEtiology_R, state = DISABLED)
        self.etiologyBtn_R_3.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_4 = Radiobutton(self.BtnPanel_R, text='Femoroacetabular impingement', variable=self.etiology_R, value='3', command = self.setEtiology_R, state = DISABLED)
        self.etiologyBtn_R_4.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_5 = Radiobutton(self.BtnPanel_R, text='others', variable=self.etiology_R, value='4', command = self.setEtiology_R, state = DISABLED)
        self.etiologyBtn_R_5.pack(padx=10, pady=4, anchor=NW)
        
        # radio button: Grade
        self.gradeLb_R = Label(self.BtnPanel_R, text = 'Grade:')
        self.gradeLb_R.pack(anchor=NW)
        self.grades_R = StringVar()
        self.grades_R.set(None)
        self.gradeBtn_R_1 = Radiobutton(self.BtnPanel_R, text='1', variable=self.grades_R, value='0', command = self.setGrade_R, state = DISABLED)
        self.gradeBtn_R_1.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_2 = Radiobutton(self.BtnPanel_R, text='2', variable=self.grades_R, value='1', command = self.setGrade_R, state = DISABLED)
        self.gradeBtn_R_2.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_3 = Radiobutton(self.BtnPanel_R, text='3', variable=self.grades_R, value='2', command = self.setGrade_R, state = DISABLED)
        self.gradeBtn_R_3.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_4 = Radiobutton(self.BtnPanel_R, text='4', variable=self.grades_R, value='3', command = self.setGrade_R, state = DISABLED)
        self.gradeBtn_R_4.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_5 = Radiobutton(self.BtnPanel_R, text='5', variable=self.grades_R, value='4', command = self.setGrade_R, state = DISABLED)
        self.gradeBtn_R_5.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_6 = Radiobutton(self.BtnPanel_R, text='Not specified', variable=self.grades_R, value='5', command = self.setGrade_R, state = DISABLED)
        self.gradeBtn_R_6.pack(padx=10, pady=4, anchor=NW)

        # canvas for cropped image
        self.subPanel_R = Canvas(self.frame, cursor = 'tcross')
        self.subPanel_R.grid(row = 5, column = 1, rowspan = 2, columnspan = 2, sticky = E)


        # >>>>>>> [BOTTOM PART] <<<<<<<
        # control panel for image navigation
        self.progLabel = Label(self.frame, text = "Progress:     /    ")
        self.progLabel.grid(row = 8, column = 0, sticky = W+N)
        self.filenameLabel = Label(self.frame, text = "PatientID:")
        self.filenameLabel.grid(row = 8, column = 1, sticky = W+N)
        self.prevBtn = Button(self.frame, text='<< Prev', width = 10, command = self.prevImage, state = DISABLED)
        self.prevBtn.grid(row = 8, column = 2, sticky = W+N)
        self.nextBtn = Button(self.frame, text='Next >>', width = 10, command = self.nextImage, state = DISABLED)
        self.nextBtn.grid(row = 8, column = 3, sticky = W+N)
        self.deLabelBtn = Button(self.frame, text='Delete-Label', width = 10, command = self.deleteLabel, state = DISABLED)
        self.deLabelBtn.grid(row = 8, column = 4, sticky = W+N)
        self.disp = Label(self.frame, text='')
        self.disp.grid(row = 8, column = 5, sticky = E+N)


    # [Button Function]   
    def setEtiology_L(self):
        self.etiologyBtn_L_1.config(state=NORMAL)
        self.etiologyBtn_L_2.config(state=NORMAL)
        self.etiologyBtn_L_3.config(state=NORMAL)
        self.etiologyBtn_L_4.config(state=NORMAL)
        self.etiologyBtn_L_5.config(state=NORMAL)
        
    def setGrade_L(self):
        self.gradeBtn_L_1.config(state=NORMAL)
        self.gradeBtn_L_2.config(state=NORMAL)
        self.gradeBtn_L_3.config(state=NORMAL)
        self.gradeBtn_L_4.config(state=NORMAL)
        self.gradeBtn_L_5.config(state=NORMAL)
        self.gradeBtn_L_6.config(state=NORMAL)

    def setEtiology_R(self):
        self.etiologyBtn_R_1.config(state=NORMAL)
        self.etiologyBtn_R_2.config(state=NORMAL)
        self.etiologyBtn_R_3.config(state=NORMAL)
        self.etiologyBtn_R_4.config(state=NORMAL)
        self.etiologyBtn_R_5.config(state=NORMAL)
        
    def setGrade_R(self):
        self.gradeBtn_R_1.config(state=NORMAL)
        self.gradeBtn_R_2.config(state=NORMAL)
        self.gradeBtn_R_3.config(state=NORMAL)
        self.gradeBtn_R_4.config(state=NORMAL)
        self.gradeBtn_R_5.config(state=NORMAL)
        self.gradeBtn_R_6.config(state=NORMAL)

    # Valid list for entry object to restrict some characters.
    '''
    def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if text in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ':
            try:
                return True
            except ValueError:
                return False
        else:
            return False
    '''

    # [Control GUI]
    def enClrSavGUI(self):
        self.btnClear.config(state=NORMAL)
        self.doneBtn.config(state=NORMAL)

    def reRadioBtn(self):
        self.etiology_L.set(None)
        self.etiology_R.set(None)
        self.grades_L.set(None)
        self.grades_R.set(None)
        self.setEtiology_L()
        self.setEtiology_R()
        self.setGrade_L()
        self.setGrade_R()

    def disRadioBtn(self):
        self.etiologyBtn_L_1.config(state=DISABLED)
        self.etiologyBtn_L_2.config(state=DISABLED)
        self.etiologyBtn_L_3.config(state=DISABLED)
        self.etiologyBtn_L_4.config(state=DISABLED)
        self.etiologyBtn_L_5.config(state=DISABLED)
        self.gradeBtn_L_1.config(state=DISABLED)
        self.gradeBtn_L_2.config(state=DISABLED)
        self.gradeBtn_L_3.config(state=DISABLED)
        self.gradeBtn_L_4.config(state=DISABLED)
        self.gradeBtn_L_5.config(state=DISABLED)
        self.gradeBtn_L_6.config(state=DISABLED)
        self.etiologyBtn_R_1.config(state=DISABLED)
        self.etiologyBtn_R_2.config(state=DISABLED)
        self.etiologyBtn_R_3.config(state=DISABLED)
        self.etiologyBtn_R_4.config(state=DISABLED)
        self.etiologyBtn_R_5.config(state=DISABLED)
        self.gradeBtn_R_1.config(state=DISABLED)
        self.gradeBtn_R_2.config(state=DISABLED)
        self.gradeBtn_R_3.config(state=DISABLED)
        self.gradeBtn_R_4.config(state=DISABLED)
        self.gradeBtn_R_5.config(state=DISABLED)
        self.gradeBtn_R_6.config(state=DISABLED)

    def initStateGUI(self):
        self.disRadioBtn()
        self.btnClear.config(state=DISABLED)
        self.doneBtn.config(state=DISABLED)
        self.prevBtn.config(state=DISABLED)
        self.nextBtn.config(state=DISABLED)
        self.deLabelBtn.config(state=DISABLED)

    def enPreNexGUI(self):
        self.prevBtn.config(state=NORMAL)
        self.nextBtn.config(state=NORMAL)
        #self.deLabelBtn.config(state=NORMAL)


    # [Load Image]
    def selectSrcDir(self):
        path = filedialog.askdirectory(title="Select image source folder", initialdir=self.svSourcePath.get())
        self.svSourcePath.set(path)
        self.loadUnLabelImg()
        return
    '''
    def selectLoadDir(self):
        path = filedialog.askdirectory(title="Select image source folder", initialdir=self.svLoadPath.get())
        self.svLoadPath.set(path)
        self.loadLabeledImg()
        return
    '''
    def loadUnLabelImg(self):
        self.loadLabelOnly = 0
        self.parent.focus()

        if not os.path.isdir(self.svSourcePath.get()):
            messagebox.showerror("Error!", message = "The specified dir doesn't exist!")
            return

        fileDir = self.svSourcePath.get()
        xlsDir = os.path.join(fileDir, 'HumanOA_Annotation_masterTable_1001_2019.xls')
        df = pd.read_excel(open(xlsDir,'rb'), sheet_name=0)
        self.idArray = df.loc[:,['PatientID', 'MatchId']].dropna()
        
        # count total before deduction done list
        self.cur   = 1
        self.count = 1
        self.total = len(self.idArray.loc[:,])

        _imgDirList     = (fileDir + '/').split() * self.total
        _imgIdList      = self.idArray['PatientID'].tolist()
        _matchimgIdList = self.idArray['MatchId'].tolist()
        _filenameExt    = '.jpg'.split() * self.total        
        self.imageList      = [x+y+z for x,y,z in zip(_imgDirList, _imgIdList, _filenameExt)]
        self.matchimageList = [x+y+z for x,y,z in zip(_imgDirList, _matchimgIdList, _filenameExt)]

        # set up output label dir the same as svSourcePath
        self.outDir = fileDir + '/Labels'
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        
        # load json file, compare images file list with json
        doneList = []
        undoneList = []
        labeled_json = self.outDir + '/'
        json_files = [pos_json for pos_json in os.listdir(labeled_json) if pos_json.endswith('.json')]

        if len(json_files) > 0:
            for i, name in enumerate(json_files):
                for j, full in enumerate(self.imageList):
                    if name.split('.')[0] in full:
                        doneList.append(full)
            undoneList = [i for i in self.imageList if not i in doneList or doneList.remove(i)]
            self.imageList = undoneList

        self.undone = len(self.imageList)
        if self.undone == 0:
            self.labelFinished()
        else:
            self.loadImage()
        print('%d images loaded from %s, still %s undone' %(self.total, fileDir, self.undone))
        
        self.initStateGUI()
        self.reRadioBtn()
        self.enPreNexGUI()
        self.enClrSavGUI()
    '''
    def loadLabeledImg(self):
        self.loadLabelOnly = 1
        self.parent.focus()
        self.imageDir = self.svLoadPath.get()
        self.imageList = []
        if not os.path.isdir(self.imageDir):
            messagebox.showerror("Error!", message = "The specified dir doesn't exist!")
            return

        windowtlist = ["*.JPEG", "*.JPG", "*.PNG", "*.BMP"]
        otherOslist = ["*.JPEG", "*.jpeg", "*.JPG", "*.jpg", "*.PNG", "*.png", "*.BMP", "*.bmp"]
        if platform.system() == 'Windows':
            extlist = windowtlist
        else:
            extlist = otherOslist

        for e in extlist:
            filelist = glob.glob(os.path.join(self.imageDir, e))
            self.imageList.extend(filelist)

        if len(self.imageList) == 0:
            messagebox.showerror("Error!", message = "No images found in the specified dir!")
            return

        # count total before deduction done list
        self.cur = 1
        self.count = 1
        self.total = len(self.imageList)
        self.imageList.sort()

        # set up output label dir the same as svSourcePath
        self.outDir = self.svLoadPath.get() + '/Labels'
        if not os.path.exists(self.outDir):
            messagebox.showerror("Error!", message = "No Labels!")
            return

        # load json file, compare images file list with json
        doneList = []
        labeled_json = self.outDir + '/'
        json_files = [pos_json for pos_json in os.listdir(labeled_json) if pos_json.endswith('.json')]
        if len(json_files) > 0:
            for i, name in enumerate(json_files):
                for j, full in enumerate(self.imageList):
                    if name.split('.')[0] in full:
                        doneList.append(full)

        if len(doneList) == 0:
            messagebox.showerror("Error!", message = "No images has been labeled!")
            return
        self.imageList = doneList
        self.loadImage()
        self.enPreNexGUI()
        self.reRadioBtn()
        self.loadLabel()
        '''
    def loadImage(self):
        # load image & directory information
        # load image to main panel canvas
        imagepath      = self.imageList[self.cur - 1]
        matchimagepath = self.matchimageList[self.cur -1]


        matchimagepath_list = matchimagepath.split('/')
        matchimgID = matchimagepath_list.pop()
        matchimgID = matchimgID[:-4]
        self.matchID = "Match ID: " + matchimgID
        self.matchIDLb.config(text=self.matchID)

        print('>>>>>>>>', self.matchID)
        self.imgInfo.append(imagepath)

        if not os.path.isfile(imagepath):
            print('>>>>>>Image {} does not exist.<<<<<<'.format(imagepath))
            messagebox.showerror("Error!", message = "The image does not exist!")
            return

        self.img = Image.open(imagepath)
        size = self.img.size
        long_side = 500

        if size[0] >= size[1]:
            self.factor = long_side / size[0]
            self.img = self.img.resize((500, int(size[1]*self.factor)))
        else:
            self.factor = long_side / size[1]
            self.img = self.img.resize((int(size[0]*self.factor), 500))
        #print('Resize factor = ', self.factor, ' Original size = ', size, ' Current size = ', self.img.size)

        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), PSIZE), height = max(self.tkimg.height(), PSIZE))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

        # load image to sub panel canvas
        imagepath_list = imagepath.split('/')
        image_id = imagepath_list.pop()
        image_id = image_id[:-4]
        #imagepath_list.pop()
        
        def listToString(li):  
            str1 = '/'
            return (str1.join(li)) 
        
        subimagepath_L = listToString(imagepath_list) + '/crop/' + image_id + '_R.jpg'
        subimagepath_R = subimagepath_L[:-5] + 'L.jpg'

        if (os.path.isfile(subimagepath_R) and os.path.isfile(subimagepath_L)):
            with Image.open(subimagepath_L) as img_L:
                self.img_L = img_L
                self.img_L = self.img_L.resize((300, 300))
                self.tkimg_L = ImageTk.PhotoImage(self.img_L)
                self.subPanel_L.config(width = 300, height = 300)
                self.subPanel_L.create_image(0, 0, image = self.tkimg_L, anchor=NW)
            
            with Image.open(subimagepath_R) as img_R:
                self.img_R = img_R
                self.img_R = self.img_R.resize((300, 300))
                self.tkimg_R = ImageTk.PhotoImage(self.img_R)
                self.subPanel_R.config(width = 300, height = 300)
                self.subPanel_R.create_image(0, 0, image = self.tkimg_R, anchor=NW)
        else:
            self.subPanel_L.delete('all')
            self.subPanel_R.delete('all')

        if os.path.isfile(matchimagepath):
            self.matchImg = Image.open(matchimagepath)
            size = self.matchImg.size
            long_side = 300

            if size[0] >= size[1]:
                factor = long_side / size[0]
                self.matchImg = self.matchImg.resize((300, int(size[1]*factor)))
            else:
                factor = long_side / size[1]
                self.matchImg = self.matchImg.resize((int(size[0]*factor), 300))
            self.tkimg_match = ImageTk.PhotoImage(self.matchImg)

            self.matchimgPanel.config(width = 300, height = 300)            
            self.matchimgPanel.create_image(0, 0, image = self.tkimg_match, anchor=NW)
        else:
            self.matchimgPanel.delete('all')


        if self.loadLabelOnly == 1:
            self.progLabel.config(text = "%04d/%04d" %(self.cur, len(self.imageList)))
        else:
            self.progLabel.config(text = "%04d/%04d" %(self.cur, self.undone))
        
        self.area = self.tkimg.width() * self.tkimg.height()
        self.imagename = image_id
        self.filenameLabel.config(text = "PatientID : %s" %(self.imagename))

    def loadLabel(self):
        imagepath = self.imageList[self.cur - 1]
        imagepath_list = imagepath.split('/')
        image_id = imagepath_list.pop()
        image_id = image_id[:-4]
        self.imagename = image_id
        self.filenameLabel.config(text = "PatientID : %s" %(self.imagename))
       
        def listToString(li):  
            str1 = '/'
            return (str1.join(li)) 
        
        LabelFile = listToString(imagepath_list) + '/Labels/' + image_id + '.json'

        if os.path.isfile(LabelFile):
            with open(LabelFile, 'r') as f:
                data = json.load(f)
                self.etiology_L.set(data[self.imagename]['etiology_l'])
                self.etiology_R.set(data[self.imagename]['etiology_r'])
                self.grades_L.set(data[self.imagename]['grades_l'])
                self.grades_R.set(data[self.imagename]['grades_r'])

            
    def prevImage(self, event = None):
        if self.cur > 1:
            self.reRadioBtn()
            self.cur -= 1
            self.loadImage()
            self.loadLabel()

    def nextImage(self, event = None):
        if self.cur < len(self.imageList):
            self.reRadioBtn()
            self.cur += 1
            self.loadImage()
            self.loadLabel()

    def deleteLabel(self):
        self.mainPanel.delete('all')
        self.subPanel_L.delete('all')
        self.subPanel_R.delete('all')
        self.reRadioBtn()
        self.disRadioBtn()
        LabelFile = self.svLoadPath.get() + '/Labels/' + self.imagename + '.json'
        os.remove(LabelFile)
        print('Image No. %s Label has been deleted.' %(self.imagename))

    def confirmPhoto(self):
        # must complete label before pressing save button
        if (self.grades_L.get() == 'None') or (self.grades_R.get() == 'None') \
            or (self.etiology_L.get() == 'None') or (self.etiology_R.get() == 'None'):
            return
        
        self.updateImageDic()
        self.reRadioBtn()
        self.loadLabel()


    def popup_ok(self):
        self.popupWindow.destroy()
        if self.WindwType == 'BBOX_OK':
            self.reRadioBtn()
            self.disRadioBtn()
            self.enClrSavGUI()
        else:
            self.updateImageDic()

    def popup_cancel(self):
        self.popupWindow.destroy()
        self.reRadioBtn()
        self.enClrSavGUI()
        if self.WindwType == 'BBOX_OK':
            self.popLastList()
            self.bboxBtn.config(state=NORMAL)
    
    def appendToList(self):
        self.classList.append(self.infoClass)
        self.ageList.append(self.infoAge)

    def popLastList(self):
        self.classList = self.classList[:-1]
        self.ageList = self.ageList[:-1]

    def printAllList(self):
        print(self.imgInfo)
        print(self.classList)
        print(self.ageList)

    def updateImageDic(self):
        print (">>>> updateImageDic")
        img_dict = {}
        data = {}
        
        data['path'] = self.imgInfo[0]
        data['etiology_r'] = self.etiology_R.get()
        data['grades_r'] = self.grades_R.get()
        data['etiology_l'] = self.etiology_L.get()
        data['grades_l'] = self.grades_L.get()

        img_dict[self.imagename] = data
        self.labelfilename = self.outDir + '/' + self.imagename +  '.json'
        with open(self.labelfilename, 'w') as outfile:
            json.dump(img_dict, outfile, indent = 4)
        print('Image No. %d saved' %(self.cur))
        print ('cur:', self.cur, 'count: ', self.count)

        self.imgInfo = []
        self.cur += 1
        self.count += 1
        if self.cur <= self.undone:
            self.loadImage()
        else:
            self.labelFinished()

    def labelFinished(self):
        NORM_FONT = ("Helvetica", 10)
        FinishWindow = Toplevel(self.parent)
        FinishWindow.geometry("%dx%d" % (400, 200))
        FinishLabel = Label(FinishWindow, text="Finish All Images.", font=NORM_FONT)
        FinishLabel.pack(side="top", fill="x", pady=10)
        ExitBtn = Button(FinishWindow, text="Exit", height=4, command = root.destroy)
        ExitBtn.pack()


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
