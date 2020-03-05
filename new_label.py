from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import Toplevel
from PIL import Image, ImageTk
import datetime
import os
import glob
import json
import pandas as pd
import time

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

        # initialize global state
        self.imgPathList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.imageID = ''
        self.labelfilename = ''
        self.tkimg = None
        self.imgInfo = []

        # ----------------- GUI stuff ---------------------
        # >>>>>>> [UPPER PART] <<<<<<<
        # button: Load Image
        self.srcDirBtn = Button(self.frame, text = "Image Folder", command = self.selectSrcDir, width = 10)
        self.srcDirBtn.grid(row = 0, column = 0, sticky = E)
        self.svSourcePath = StringVar()
        self.svSourcePath.set(os.getcwd())
        self.entrySrcDir = Entry(self.frame, textvariable = self.svSourcePath)
        self.entrySrcDir.grid(row = 0, column = 1, columnspan=4, sticky = W+E)

        # >>>>>>> [CENTER PART] <<<<<<<
        # canvas for original image
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
        self.matchIDLb.config(font=("Helvetica", 16))

        self.BtnPanel_L = Frame(self.frame)
        self.BtnPanel_L.grid(row = 4, column = 5, rowspan = 4, sticky = NW)
        self.sideLb_L = Label(self.BtnPanel_L, text = 'Left')
        self.sideLb_L.pack(anchor=NW)
        self.sideLb_L.config(font=("Helvetica", 16))

        # radio button: Etiology
        self.etiologyLb_L = Label(self.BtnPanel_L, text = 'Etiology:')
        self.etiologyLb_L.pack(anchor=NW)
        self.etiology_L = StringVar()
        self.etiology_L.set(None)
        self.etiologyBtn_L_1 = Radiobutton(self.BtnPanel_L, text='Osteonecrosis', variable=self.etiology_L, value='0', command = self.setEtiologyBtn_L, state = DISABLED)
        self.etiologyBtn_L_1.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_2 = Radiobutton(self.BtnPanel_L, text='Avascular necrosis', variable=self.etiology_L, value='1', command = self.setEtiologyBtn_L, state = DISABLED)
        self.etiologyBtn_L_2.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_3 = Radiobutton(self.BtnPanel_L, text='Osteoarthritis', variable=self.etiology_L, value='2', command = self.setEtiologyBtn_L, state = DISABLED)
        self.etiologyBtn_L_3.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_4 = Radiobutton(self.BtnPanel_L, text='Femoroacetabular impingement', variable=self.etiology_L, value='3', command = self.setEtiologyBtn_L, state = DISABLED)
        self.etiologyBtn_L_4.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_5 = Radiobutton(self.BtnPanel_L, text='others', variable=self.etiology_L, value='4', command = self.setEtiologyBtn_L, state = DISABLED)
        self.etiologyBtn_L_5.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_6 = Radiobutton(self.BtnPanel_L, text='Fracture', variable=self.etiology_L, value='5', command = self.setEtiologyBtn_L, state = DISABLED)
        self.etiologyBtn_L_6.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_7 = Radiobutton(self.BtnPanel_L, text='Normal', variable=self.etiology_L, value='6', command = self.setEtiologyBtn_L, state = DISABLED)
        self.etiologyBtn_L_7.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_L_8 = Radiobutton(self.BtnPanel_L, text='Joint or nail', variable=self.etiology_L, value='7', command = self.setEtiologyBtn_L, state = DISABLED)
        self.etiologyBtn_L_8.pack(padx=10, pady=4, anchor=NW)

        # radio button: Grade
        self.gradeLb_L = Label(self.BtnPanel_L, text = 'Grade:')
        self.gradeLb_L.pack(anchor=NW)
        self.grades_L = StringVar()
        self.grades_L.set(None)
        self.gradeBtn_L_1 = Radiobutton(self.BtnPanel_L, text='1', variable=self.grades_L, value='0', command = self.setGradeBtn_L, state = DISABLED)
        self.gradeBtn_L_1.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_2 = Radiobutton(self.BtnPanel_L, text='2', variable=self.grades_L, value='1', command = self.setGradeBtn_L, state = DISABLED)
        self.gradeBtn_L_2.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_3 = Radiobutton(self.BtnPanel_L, text='3', variable=self.grades_L, value='2', command = self.setGradeBtn_L, state = DISABLED)
        self.gradeBtn_L_3.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_4 = Radiobutton(self.BtnPanel_L, text='4', variable=self.grades_L, value='3', command = self.setGradeBtn_L, state = DISABLED)
        self.gradeBtn_L_4.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_5 = Radiobutton(self.BtnPanel_L, text='5', variable=self.grades_L, value='4', command = self.setGradeBtn_L, state = DISABLED)
        self.gradeBtn_L_5.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_L_6 = Radiobutton(self.BtnPanel_L, text='Not specified', variable=self.grades_L, value='5', command = self.setGradeBtn_L, state = DISABLED)
        self.gradeBtn_L_6.pack(padx=10, pady=4, anchor=NW)

        # canvas for cropped image
        self.subPanel_L = Canvas(self.frame, cursor = 'tcross')
        self.subPanel_L.grid(row = 5, column = 3, rowspan = 2, columnspan = 2, sticky = W)

        # control button
        self.clrBtn = Button(self.BtnPanel_L, text = 'Clear All', width = 20, height = 2, command = self.reRadioBtn, state = DISABLED)
        self.clrBtn.pack()
        self.doneBtn = Button(self.BtnPanel_L, text = 'Save annotation', width = 20, height = 5, command = self.confirmImage, fg='red', state = DISABLED)
        self.doneBtn.pack()

        # >>>>>>> [LEFT PART] <<<<<<<
        # left side of GUI, right side of patient in x-ray
        self.GotoPanel = Frame(self.frame)
        self.GotoPanel.grid(row = 1, column=0, rowspan = 3, sticky = NW)
        self.gotoLb = Label(self.GotoPanel, text = 'PatientID:')
        self.gotoLb.pack(anchor=NW)
        self.gotoText = StringVar(self.GotoPanel)
        self.gotoText.set('000000_01A') 
        vcmd = (self.GotoPanel.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.gotoEtr = Entry(self.GotoPanel, validate = 'key', validatecommand = vcmd, textvariable=self.gotoText)
        self.gotoEtr.pack(anchor=NW)
        self.gotoBtn = Button(self.GotoPanel, text = 'GO', width = 5, height = 1, command = self.gotoImage, state = DISABLED)
        self.gotoBtn.pack(anchor=NW)

        self.BtnPanel_R = Frame(self.frame)
        self.BtnPanel_R.grid(row = 4, column = 0, rowspan = 4, sticky = NE)
        self.sideLb_R = Label(self.BtnPanel_R, text = 'Right')
        self.sideLb_R.pack(anchor=NW)
        self.sideLb_R.config(font=("Courier", 16))

        # radio button: Etiology
        self.etiologyLb_R = Label(self.BtnPanel_R, text = 'Etiology:')
        self.etiologyLb_R.pack(anchor=NW)
        self.etiology_R = StringVar()
        self.etiology_R.set(None)
        self.etiologyBtn_R_1 = Radiobutton(self.BtnPanel_R, text='Osteonecrosis', variable=self.etiology_R, value='0', command = self.setEtiologyBtn_R, state = DISABLED)
        self.etiologyBtn_R_1.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_2 = Radiobutton(self.BtnPanel_R, text='Avascular necrosis', variable=self.etiology_R, value='1', command = self.setEtiologyBtn_R, state = DISABLED)
        self.etiologyBtn_R_2.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_3 = Radiobutton(self.BtnPanel_R, text='Osteoarthritis', variable=self.etiology_R, value='2', command = self.setEtiologyBtn_R, state = DISABLED)
        self.etiologyBtn_R_3.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_4 = Radiobutton(self.BtnPanel_R, text='Femoroacetabular impingement', variable=self.etiology_R, value='3', command = self.setEtiologyBtn_R, state = DISABLED)
        self.etiologyBtn_R_4.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_5 = Radiobutton(self.BtnPanel_R, text='others', variable=self.etiology_R, value='4', command = self.setEtiologyBtn_R, state = DISABLED)
        self.etiologyBtn_R_5.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_6 = Radiobutton(self.BtnPanel_R, text='Fracture', variable=self.etiology_R, value='5', command = self.setEtiologyBtn_R, state = DISABLED)
        self.etiologyBtn_R_6.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_7 = Radiobutton(self.BtnPanel_R, text='Normal', variable=self.etiology_R, value='6', command = self.setEtiologyBtn_R, state = DISABLED)
        self.etiologyBtn_R_7.pack(padx=10, pady=4, anchor=NW)
        self.etiologyBtn_R_8 = Radiobutton(self.BtnPanel_R, text='Joint or nail', variable=self.etiology_R, value='7', command = self.setEtiologyBtn_R, state = DISABLED)
        self.etiologyBtn_R_8.pack(padx=10, pady=4, anchor=NW)
        
        # radio button: Grade
        self.gradeLb_R = Label(self.BtnPanel_R, text = 'Grade:')
        self.gradeLb_R.pack(anchor=NW)
        self.grades_R = StringVar()
        self.grades_R.set(None)
        self.gradeBtn_R_1 = Radiobutton(self.BtnPanel_R, text='1', variable=self.grades_R, value='0', command = self.setGradeBtn_R, state = DISABLED)
        self.gradeBtn_R_1.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_2 = Radiobutton(self.BtnPanel_R, text='2', variable=self.grades_R, value='1', command = self.setGradeBtn_R, state = DISABLED)
        self.gradeBtn_R_2.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_3 = Radiobutton(self.BtnPanel_R, text='3', variable=self.grades_R, value='2', command = self.setGradeBtn_R, state = DISABLED)
        self.gradeBtn_R_3.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_4 = Radiobutton(self.BtnPanel_R, text='4', variable=self.grades_R, value='3', command = self.setGradeBtn_R, state = DISABLED)
        self.gradeBtn_R_4.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_5 = Radiobutton(self.BtnPanel_R, text='5', variable=self.grades_R, value='4', command = self.setGradeBtn_R, state = DISABLED)
        self.gradeBtn_R_5.pack(padx=10, pady=4, anchor=NW)
        self.gradeBtn_R_6 = Radiobutton(self.BtnPanel_R, text='Not specified', variable=self.grades_R, value='5', command = self.setGradeBtn_R, state = DISABLED)
        self.gradeBtn_R_6.pack(padx=10, pady=4, anchor=NW)
        
        # skip button for unknown annotation
        self.skipBtn = Button(self.BtnPanel_R, text = 'Unknown Annotation\n Skip This Image', width = 20, height = 3, command = self.skipImage, fg='red',state = DISABLED)
        self.skipBtn.pack(padx=10, pady=20, anchor=SW)

        # canvas for cropped image
        self.subPanel_R = Canvas(self.frame, cursor = 'tcross')
        self.subPanel_R.grid(row = 5, column = 1, rowspan = 2, columnspan = 2, sticky = E)
        
        # >>>>>>> [BOTTOM PART] <<<<<<<
        # control panel for image navigation
        self.progLb = Label(self.frame, text = "Progress:     /    ")
        self.progLb.grid(row = 8, column = 0, sticky = SW)
        self.filenameLabel = Label(self.frame, text = "PatientID:")
        self.filenameLabel.grid(row = 8, column = 1, sticky = SW)
        self.filenameLabel.config(font=("Helvetica", 16))
        self.prevBtn = Button(self.frame, text='<< Prev', width = 10, command = self.prevImage, state = DISABLED)
        self.prevBtn.grid(row = 8, column = 2, sticky = SW)
        self.nextBtn = Button(self.frame, text='Next >>', width = 10, command = self.nextImage, state = DISABLED)
        self.nextBtn.grid(row = 8, column = 3, sticky = SW)
        self.statusLb = Label(self.frame, text = 'Unlabeled')
        self.statusLb.grid(row = 8, column = 4, sticky = SW)

    # [Button Function]   
    def setEtiologyBtn_L(self):
        self.etiologyBtn_L_1.config(state=NORMAL)
        self.etiologyBtn_L_2.config(state=NORMAL)
        self.etiologyBtn_L_3.config(state=NORMAL)
        self.etiologyBtn_L_4.config(state=NORMAL)
        self.etiologyBtn_L_5.config(state=NORMAL)
        self.etiologyBtn_L_6.config(state=NORMAL)
        self.etiologyBtn_L_7.config(state=NORMAL)
        self.etiologyBtn_L_8.config(state=NORMAL)
        
    def setGradeBtn_L(self):
        self.gradeBtn_L_1.config(state=NORMAL)
        self.gradeBtn_L_2.config(state=NORMAL)
        self.gradeBtn_L_3.config(state=NORMAL)
        self.gradeBtn_L_4.config(state=NORMAL)
        self.gradeBtn_L_5.config(state=NORMAL)
        self.gradeBtn_L_6.config(state=NORMAL)

    def setEtiologyBtn_R(self):
        self.etiologyBtn_R_1.config(state=NORMAL)
        self.etiologyBtn_R_2.config(state=NORMAL)
        self.etiologyBtn_R_3.config(state=NORMAL)
        self.etiologyBtn_R_4.config(state=NORMAL)
        self.etiologyBtn_R_5.config(state=NORMAL)
        self.etiologyBtn_R_6.config(state=NORMAL)
        self.etiologyBtn_R_7.config(state=NORMAL)
        self.etiologyBtn_R_8.config(state=NORMAL)
        
    def setGradeBtn_R(self):
        self.gradeBtn_R_1.config(state=NORMAL)
        self.gradeBtn_R_2.config(state=NORMAL)
        self.gradeBtn_R_3.config(state=NORMAL)
        self.gradeBtn_R_4.config(state=NORMAL)
        self.gradeBtn_R_5.config(state=NORMAL)
        self.gradeBtn_R_6.config(state=NORMAL)

    # Valid list for entry object to restrict some characters.
    def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if text in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789':
            try:
                return True
            except ValueError:
                return False
        else:
            return False

    # [Control GUI]
    def enBtn(self):
        self.clrBtn.config(state=NORMAL)
        self.doneBtn.config(state=NORMAL)
        self.prevBtn.config(state=NORMAL)
        self.nextBtn.config(state=NORMAL)
        self.skipBtn.config(state=NORMAL)
        self.gotoBtn.config(state=NORMAL)

    def reRadioBtn(self):
        self.etiology_L.set(None)
        self.etiology_R.set(None)
        self.grades_L.set(None)
        self.grades_R.set(None)
        self.setEtiologyBtn_L()
        self.setEtiologyBtn_R()
        self.setGradeBtn_L()
        self.setGradeBtn_R()

    def disRadioBtn(self):
        self.etiologyBtn_L_1.config(state=DISABLED)
        self.etiologyBtn_L_2.config(state=DISABLED)
        self.etiologyBtn_L_3.config(state=DISABLED)
        self.etiologyBtn_L_4.config(state=DISABLED)
        self.etiologyBtn_L_5.config(state=DISABLED)
        self.etiologyBtn_L_6.config(state=DISABLED)
        self.etiologyBtn_L_7.config(state=DISABLED)
        self.etiologyBtn_L_8.config(state=DISABLED)
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
        self.etiologyBtn_R_6.config(state=DISABLED)
        self.etiologyBtn_R_7.config(state=DISABLED)
        self.etiologyBtn_R_8.config(state=DISABLED)
        self.gradeBtn_R_1.config(state=DISABLED)
        self.gradeBtn_R_2.config(state=DISABLED)
        self.gradeBtn_R_3.config(state=DISABLED)
        self.gradeBtn_R_4.config(state=DISABLED)
        self.gradeBtn_R_5.config(state=DISABLED)
        self.gradeBtn_R_6.config(state=DISABLED)

    def disCanvas(self):
        self.mainPanel.delete(ALL)
        self.matchimgPanel.delete(ALL)
        self.subPanel_L.delete(ALL)
        self.subPanel_R.delete(ALL)

    def initStateGUI(self):
        self.disRadioBtn()
        self.clrBtn.config(state=DISABLED)
        self.doneBtn.config(state=DISABLED)
        self.prevBtn.config(state=DISABLED)
        self.nextBtn.config(state=DISABLED)

    # [Load Image]
    def selectSrcDir(self):
        path = filedialog.askdirectory(title="Select image source folder", initialdir=self.svSourcePath.get())
        self.svSourcePath.set(path)
        self.initLoadImg()
        return

    def initLoadImg(self):
        self.parent.focus()

        if not os.path.isdir(self.svSourcePath.get()):
            messagebox.showerror("Error!", message = "The specified dir doesn't exist!")
            return

        fileDir = self.svSourcePath.get()

        # set up output label diretory
        self.outDir = fileDir + '/labels'
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        
        # dirty work
        # json
        labelDir = self.outDir + '/'
        labelIDList = [os.path.splitext(pos_json)[0] for pos_json in os.listdir(labelDir) if pos_json.endswith('.json')]
        self.cur = len(labelIDList) + 1

        # xls
        xlsDir = os.path.join(fileDir, 'HumanOA_Annotation_masterTable_0225_2020.xls')
        df = pd.read_excel(open(xlsDir,'rb'), sheet_name=0)
        self.masterTable = df.loc[:,['PatientID', 'MatchId']]
        labelTable = self.masterTable.copy()
        unlabelTable = self.masterTable.copy()
        labelTable = labelTable[labelTable['PatientID'].isin(labelIDList)]
        unlabelTable = unlabelTable[~unlabelTable['PatientID'].isin(labelIDList)]
        self.masterTable = pd.concat([labelTable, unlabelTable], ignore_index=True, sort =False)
        
        self.total = len(self.masterTable)
        self.masterTable['MatchId'] = self.masterTable['MatchId'].fillna('None')
        self.imgIDList = self.masterTable['PatientID'].tolist()

        # make image path list
        self.imgParDir = fileDir + '/original/'
        _imgParDirList = self.imgParDir.split() * self.total
        _imgNameExtList = '.jpg'.split() * self.total       
        self.imgPathList = [x+y+z for x,y,z in zip(_imgParDirList, self.imgIDList, _imgNameExtList)]
        
        if self.cur == self.total + 1:
            self.labelFinished()
        else:
            self.loadImage()
        print('%d images loaded from %s, %s images have been annotated' %(self.total, fileDir, self.cur-1))
        
        self.initStateGUI()
        self.reRadioBtn()
        self.enBtn()
    
    def loadImage(self):
        self.disCanvas()

        imagepath  = self.imgPathList[self.cur - 1]
        self.imgInfo.clear
        self.imgInfo.append(imagepath)
        self.matchimgID = self.masterTable.at[self.cur-1, 'MatchId']
        matchimgpath = ''

        if self.matchimgID != 'None':
            matchimgpath = self.imgParDir + self.matchimgID + '.jpg'
            self.matchID = "Match ID: " + self.matchimgID
        else:
            self.matchID = "No match image"
        self.matchIDLb.config(text=self.matchID)

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

        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), PSIZE), height = max(self.tkimg.height(), PSIZE))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

        # load image to sub panel canvas
        imagepath_list = imagepath.split('/')
        _image_id = imagepath_list.pop()
        _image_id = _image_id[:-4]
        imagepath_list.pop()
        
        def listToString(li):  
            str1 = '/'
            return (str1.join(li)) 
        
        subimagepath_L = listToString(imagepath_list) + '/crop/' + _image_id + '_R.jpg'
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
            self.subPanel_L.delete(ALL)
            self.subPanel_R.delete(ALL)

        if os.path.isfile(matchimgpath):
            with Image.open(matchimgpath) as matchImg:
                self.matchImg = matchImg
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
            self.matchimgPanel.delete(ALL)

        self.progLb.config(text = "%04d/%04d" %(self.cur, self.total))
        self.imageID = _image_id
        self.filenameLabel.config(text = "PatientID : %s" %(self.imageID))

    def loadLabel(self):
        imagepath = self.imgPathList[self.cur - 1]
        imagepath_list = imagepath.split('/')
        image_id = imagepath_list.pop()
        image_id = image_id[:-4]
        imagepath_list.pop()
        
        def listToString(li):  
            str1 = '/'
            return (str1.join(li)) 
        
        LabelFile = listToString(imagepath_list) + '/labels/' + image_id + '.json'
        if os.path.isfile(LabelFile):
            with open(LabelFile, 'r') as f:
                data = json.load(f)
                etiology_L = data[self.imageID]['etiology_l']
                etiology_R = data[self.imageID]['etiology_r']
                grades_L = data[self.imageID]['grades_l']
                grades_R = data[self.imageID]['grades_r']

                if (etiology_L == 'None') or (etiology_R == 'None') \
                    or (grades_L == 'None') or (grades_R == 'None'):
                    self.statusLb.config(text='Labeled as Unknown Annotation')
                else:
                    self.statusLb.config(text='Labeled')

                self.etiology_L.set(etiology_L)
                self.etiology_R.set(etiology_R)
                self.grades_L.set(grades_L)
                self.grades_R.set(grades_R)
        else:
            self.statusLb.config(text='Unlabeled')

    def prevImage(self):
        if self.cur > 1:
            self.reRadioBtn()
            self.cur -= 1
            self.loadImage()
            self.loadLabel()

    def nextImage(self):
        if self.cur < len(self.imgPathList):
            self.reRadioBtn()
            self.cur += 1
            self.loadImage()
            self.loadLabel()

    def gotoImage(self):
        gotoImageID =  self.gotoText.get()

        if len(gotoImageID) == 0:
            return
        elif gotoImageID in self.imgIDList:
            self.initLoadImg()
            self.cur = self.imgIDList.index(gotoImageID) + 1
            self.loadImage()
            self.loadLabel()
        else:
            return
        
    def confirmImage(self):
        if (self.grades_L.get() == 'None') or (self.grades_R.get() == 'None') \
            or (self.etiology_L.get() == 'None') or (self.etiology_R.get() == 'None'):
            return
        
        self.updateImageDic()
        self.reRadioBtn()
        self.loadLabel()

    def skipImage(self):
        self.reRadioBtn()
        self.updateImageDic()
        self.loadLabel()

    def updateImageDic(self):
        img_dict = {}
        data = {}
        
        data['path'] = self.imgInfo[-1]
        data['imageid'] = self.imageID
        data['matchid'] = self.matchimgID
        data['etiology_r'] = self.etiology_R.get()
        data['grades_r'] = self.grades_R.get()
        data['etiology_l'] = self.etiology_L.get()
        data['grades_l'] = self.grades_L.get()
        data['time'] = time.strftime("%b/%d/%X", time.localtime()) 

        img_dict[self.imageID] = data
        self.labelfilename = self.outDir + '/' + self.imageID +  '.json'
        with open(self.labelfilename, 'w') as outfile:
            json.dump(img_dict, outfile, indent = 4)
        print('PatientID %s saved' %(self.imageID))

        self.imgInfo = []
        self.cur += 1
        if self.cur <= self.total:
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

def jsontocsv():
    json_list = glob.glob(os.path.join(os.getcwd(), 'DoctorA', 'labels','*.json'))
    lookupTable_eti = {'None':'Unknown Annotation', '0':'Osteonecrosis', '1':'Avascular necrosis', '2':'Osteoarthritis', \
                        '3':'Femoroacetabular impingement', '4':'others', '5':'Fracture', '6':'Normal', '7':'Joint or nail'}
    lookupTable_grade = {'None':'Unknown Annotation', '0':'1', '1':'2', '2':'3', '3':'4', '4':'5', '5':'Not specified'}
    
    outputDF = pd.DataFrame(columns=['PatientID','MatchID','Etiology_right','Grades_right','Etiology_left','Grades_left','time', 'file_path'])

    for i in range(len(json_list)):
        df = pd.read_json(json_list[i], orient='values')
        image_id = json_list[i].split('/')[-1][:-5]
        
        img_id   = df[image_id]['imageid']
        match_id = df[image_id]['matchid']
        eti_r    = df[image_id]['etiology_r']
        grades_r = df[image_id]['grades_r']
        eti_l    = df[image_id]['etiology_l']
        grades_l = df[image_id]['grades_l']
        time     = df[image_id]['time']
        path     = df[image_id]['path']
       
        eti_r    = lookupTable_eti[eti_r]
        grades_r = lookupTable_grade[grades_r]
        eti_l    = lookupTable_eti[eti_l]
        grades_l = lookupTable_grade[grades_l]

        new_row = [img_id, match_id, eti_r, grades_r, eti_l, grades_l, time, path]
        
        outputDF = outputDF.append(pd.DataFrame([new_row], columns = outputDF.columns))

    outputDF.to_csv("export.csv", index=False)
    print('export all json files to report.csv')

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
    jsontocsv()