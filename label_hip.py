from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import Toplevel
from PIL import Image, ImageTk, ImageEnhance
import datetime
import os
import glob
import json
import random
import platform

# colors for the bboxes
COLORS = ['blue', 'red', 'cyan', 'orange', 'limegreen', 'hotpink', 'green', 'fuchsia',  'olive', 'darkviolet']
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

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.classIdList = []
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # reference to image and bbox info, "info" set default value
        self.imgInfo = []
        self.infoClass = 'Child'
        self.infoAge = '0-6 month'
        self.infoCovered = 'No Blanket'
        self.infoBodyLean = 'No Lean'
        self.infoBodyTwisted = 'No Twisted'
        self.infoBodyOverlap = 'No Overlap'
        self.classList = []
        self.ageList = []
        self.leanList = []
        self.twistList = []
        self.blanketList = []
        self.overlapList = []
        self.sizeList = []


        # ----------------- GUI stuff ---------------------
        # >>>>>> [UPPER PART] <<<<<<<
        # button: Load Unlabel Images
        # button: Load Labeled Images
        self.srcDirBtn = Button(self.frame, text = "Un-Label", command = self.selectSrcDir, width = 10)
        self.srcDirBtn.grid(row = 0, column = 0)
        self.svSourcePath = StringVar()
        self.svSourcePath.set(os.getcwd())
        self.entrySrcDir = Entry(self.frame, textvariable = self.svSourcePath)
        self.entrySrcDir.grid(row = 0, column = 1, columnspan=4, sticky = W+E)

        self.srcLoadBtn = Button(self.frame, text = "Labeled", command = self.selectLoadDir, width = 10)
        self.srcLoadBtn.grid(row = 1, column = 0)
        self.svLoadPath = StringVar()
        self.svLoadPath.set(os.getcwd())
        self.entryLoadDir = Entry(self.frame, textvariable = self.svLoadPath)
        self.entryLoadDir.grid(row = 1, column = 1, columnspan=4, sticky = W+E)


        # >>>>>> [CENTRE PART] <<<<<<<
        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor = 'tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)
        self.parent.bind("p", self.prevImage) # press 'p' to go backforward
        self.parent.bind("n", self.nextImage) # press 'n' to go forward
        self.mainPanel.grid(row = 2, column = 1, rowspan = 4, columnspan = 4, sticky = W+E+N+S)


        # >>>>>> [RIGHT PART] <<<<<<<
        # radio button: Class
        self.BtnPanel = Frame(self.frame)
        self.BtnPanel.grid(row = 2, column = 5, sticky = W+N)
        self.classLb = Label(self.BtnPanel, text = 'Class:')
        self.classLb.pack(anchor=NW)
        self.classname = StringVar()
        self.classname.set(None)
        self.childBtn = Radiobutton(self.BtnPanel, text='Child', variable=self.classname, value='0', command = self.setClass, state = DISABLED)
        self.childBtn.pack(padx=10, pady=2,anchor=NW)
        self.adultBtn = Radiobutton(self.BtnPanel, text='Adult', variable=self.classname, value='1', command = self.setClass, state = DISABLED)
        self.adultBtn.pack(padx=10, anchor=NW)

        # radio button: Age
        self.ageLb = Label(self.BtnPanel, text = 'Age:')
        self.ageLb.pack(anchor=NW)
        self.ages = StringVar()
        self.ages.set(None)
        self.age6mBtn = Radiobutton(self.BtnPanel, text='0-6 month', variable=self.ages, value='0', command = self.setAge, state = DISABLED)
        self.age6mBtn.pack(padx=10, pady=2, anchor=NW)
        self.age12mBtn = Radiobutton(self.BtnPanel, text='7-12 month', variable=self.ages, value='1', command = self.setAge, state = DISABLED)
        self.age12mBtn.pack(padx=10, pady=2, anchor=NW)
        self.age6yrBtn = Radiobutton(self.BtnPanel, text='12m-6 years', variable=self.ages, value='2', command = self.setAge, state = DISABLED)
        self.age6yrBtn.pack(padx=10, pady=2, anchor=NW)
        self.age6upBtn = Radiobutton(self.BtnPanel, text='6 years up', variable=self.ages, value='3', command = self.setAge, state = DISABLED)
        self.age6upBtn.pack(padx=10, pady=2, anchor=NW)

        # check button: In blanket / People overlap / People Lean / People Twisted
        self.bodylean = StringVar()
        self.bodylean.set(None)
        self.bodyleanBtn = Checkbutton(self.BtnPanel, text='is Body Lean?', variable=self.bodylean, onvalue=1, offvalue=0, command = self.setBodyLean, state = DISABLED)
        self.bodyleanBtn.pack(anchor=NW)
        self.twisted = StringVar()
        self.twisted.set(None)
        self.twistedBtn = Checkbutton(self.BtnPanel, text='is Body Twisted?', variable=self.twisted, onvalue=1, offvalue=0, command = self.setBodyTwisted, state = DISABLED)
        self.twistedBtn.pack(anchor=NW)
        self.covered = StringVar()
        self.covered.set(None)
        self.coveredBtn = Checkbutton(self.BtnPanel, text='is Baby in Blanket?', variable=self.covered, onvalue=1, offvalue=0, command = self.setBabyCovered, state = DISABLED)
        self.coveredBtn.pack(anchor=NW)
        self.overlap = StringVar()
        self.overlap.set(None)
        self.overlapBtn = Checkbutton(self.BtnPanel, text='been Covered or Overlap?', variable=self.overlap, onvalue=1, offvalue=0, command = self.setBodyOverLap, state = DISABLED)
        self.overlapBtn.pack(anchor=NW)

        # bounding boxes parts
        self.bboxBtn = Button(self.BtnPanel, text = 'BBOX OK', width = 20, height = 4, command = self.confirmBBOX, state = DISABLED)
        self.bboxBtn.pack()
        self.listbox = Listbox(self.BtnPanel, width = 25, height = 10)
        self.listbox.pack()
        self.btnDel = Button(self.BtnPanel, text = 'Delete Box', width = 20, height = 2, command = self.delBBox, state = DISABLED)
        self.btnDel.pack()
        self.btnClear = Button(self.BtnPanel, text = 'Clear All', width = 20, height = 2, command = self.clearBBox, state = DISABLED)
        self.btnClear.pack()
        self.noObjBtn = Button(self.BtnPanel, text = 'NO Objects', width = 20, height = 2, command = self.confirmNoObjPhoto)
        self.noObjBtn.pack()
        self.doneBtn = Button(self.BtnPanel, text = 'Image DONE', width = 20, height = 5, command = self.confirmPhoto, fg='red', state = DISABLED)
        self.doneBtn.pack()

        # >>>>>> [BOTTOM PART] <<<<<<<
        # control panel for image navigation
        self.progLabel = Label(self.frame, text = "Progress:     /    ")
        self.progLabel.grid(row = 10, column = 0, sticky = W+N)
        self.filenameLabel = Label(self.frame, text = "File name:")
        self.filenameLabel.grid(row = 10, column = 1, sticky = W+N)
        self.prevBtn = Button(self.frame, text='<< Prev', width = 10, command = self.prevImage, state = DISABLED)
        self.prevBtn.grid(row = 10, column = 2, sticky = W+N)
        self.nextBtn = Button(self.frame, text='Next >>', width = 10, command = self.nextImage, state = DISABLED)
        self.nextBtn.grid(row = 10, column = 3, sticky = W+N)
        self.deLabelBtn = Button(self.frame, text='Delete-Label', width = 10, command = self.deleteLabel, state = DISABLED)
        self.deLabelBtn.grid(row = 10, column = 4, sticky = W+N)
        self.disp = Label(self.frame, text='')
        self.disp.grid(row = 10, column = 5, sticky = E+N)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)


    # [Control GUI]
    def resetBtnValue(self):
        self.classname.set('0')
        self.ages.set('0')
        self.bodylean.set('0')
        self.twisted.set('0')
        self.covered.set('0')
        self.overlap.set('0')
        self.setClass()
        self.setAge()
        self.setBodyLean()
        self.setBodyTwisted()
        self.setBabyCovered()
        self.setBodyOverLap()

    def enableControlGUI(self):
        self.btnDel.config(state=NORMAL)
        self.btnClear.config(state=NORMAL)
        self.doneBtn.config(state=NORMAL)
        self.noObjBtn.config(state=DISABLED)

    def enableBottomGUI(self):
        self.childBtn.config(state=NORMAL)
        self.adultBtn.config(state=NORMAL)
        self.age6mBtn.config(state=NORMAL)
        self.age12mBtn.config(state=NORMAL)
        self.age6yrBtn.config(state=NORMAL)
        self.age6upBtn.config(state=NORMAL)
        self.coveredBtn.config(state=NORMAL)
        self.overlapBtn.config(state=NORMAL)
        self.bodyleanBtn.config(state=NORMAL)
        self.twistedBtn.config(state=NORMAL)

    def disableBottomGUI(self):
        self.childBtn.config(state=DISABLED)
        self.adultBtn.config(state=DISABLED)
        self.age6mBtn.config(state=DISABLED)
        self.age12mBtn.config(state=DISABLED)
        self.age6yrBtn.config(state=DISABLED)
        self.age6upBtn.config(state=DISABLED)
        self.coveredBtn.config(state=DISABLED)
        self.overlapBtn.config(state=DISABLED)
        self.bodyleanBtn.config(state=DISABLED)
        self.twistedBtn.config(state=DISABLED)

    def initStateGUI(self):
        self.childBtn.config(state=DISABLED)
        self.adultBtn.config(state=DISABLED)
        self.age6mBtn.config(state=DISABLED)
        self.age12mBtn.config(state=DISABLED)
        self.age6yrBtn.config(state=DISABLED)
        self.age6upBtn.config(state=DISABLED)
        self.coveredBtn.config(state=DISABLED)
        self.overlapBtn.config(state=DISABLED)
        self.bodyleanBtn.config(state=DISABLED)
        self.twistedBtn.config(state=DISABLED)
        self.btnDel.config(state=DISABLED)
        self.btnClear.config(state=DISABLED)
        self.bboxBtn.config(state=DISABLED)
        self.doneBtn.config(state=DISABLED)
        self.prevBtn.config(state=DISABLED)
        self.nextBtn.config(state=DISABLED)
        self.deLabelBtn.config(state=DISABLED)

    def disableAllGUI(self):
        self.childBtn.config(state=DISABLED)
        self.adultBtn.config(state=DISABLED)
        self.age6mBtn.config(state=DISABLED)
        self.age12mBtn.config(state=DISABLED)
        self.age6yrBtn.config(state=DISABLED)
        self.age6upBtn.config(state=DISABLED)
        self.coveredBtn.config(state=DISABLED)
        self.overlapBtn.config(state=DISABLED)
        self.bodyleanBtn.config(state=DISABLED)
        self.twistedBtn.config(state=DISABLED)
        self.btnDel.config(state=DISABLED)
        self.btnClear.config(state=DISABLED)
        self.noObjBtn.config(state=DISABLED)
        self.bboxBtn.config(state=DISABLED)
        self.doneBtn.config(state=DISABLED)
        self.prevBtn.config(state=DISABLED)
        self.nextBtn.config(state=DISABLED)
        self.deLabelBtn.config(state=DISABLED)

    def previewImageLabelGUI(self):
        self.childBtn.config(state=DISABLED)
        self.adultBtn.config(state=DISABLED)
        self.age6mBtn.config(state=DISABLED)
        self.age12mBtn.config(state=DISABLED)
        self.age6yrBtn.config(state=DISABLED)
        self.age6upBtn.config(state=DISABLED)
        self.coveredBtn.config(state=DISABLED)
        self.overlapBtn.config(state=DISABLED)
        self.bodyleanBtn.config(state=DISABLED)
        self.twistedBtn.config(state=DISABLED)
        self.btnDel.config(state=DISABLED)
        self.btnClear.config(state=DISABLED)
        self.noObjBtn.config(state=DISABLED)
        self.bboxBtn.config(state=DISABLED)
        self.doneBtn.config(state=DISABLED)
        self.prevBtn.config(state=NORMAL)
        self.nextBtn.config(state=NORMAL)
        self.deLabelBtn.config(state=NORMAL)

    # [Button Funcion]
    def setClass(self):
        if self.classname.get() == '0':
            self.infoClass = 'Child'
            self.age6mBtn.config(state=NORMAL)
            self.age12mBtn.config(state=NORMAL)
            self.age6yrBtn.config(state=NORMAL)
            self.age6upBtn.config(state=DISABLED)
        else:
            self.infoClass = 'Adult'
            self.ages.set('3')
            self.infoAge = '6 years up'
            self.age6mBtn.config(state=DISABLED)
            self.age12mBtn.config(state=DISABLED)
            self.age6yrBtn.config(state=DISABLED)
            self.age6upBtn.config(state=NORMAL)

    def setAge(self):
        if self.ages.get() == '0':
            self.infoAge = '0-6 month'
        elif self.ages.get() == '1':
            self.infoAge = '7-12 month'
        else:
            self.infoAge = '1-6 years old'

    def setBodyLean(self):
        if self.bodylean.get() == '0':
            self.infoBodyLean = 'No Lean'
        else:
            self.infoBodyLean = 'Lean'

    def setBodyTwisted(self):
        if self.twisted.get() == '0':
            self.infoBodyTwisted = 'No Twisted'
        else:
            self.infoBodyTwisted = 'Twisted'

    def setBodyOverLap(self):
        if self.overlap.get() == '0':
            self.infoBodyOverlap = 'No Overlap(Covered)'
        else:
            self.infoBodyOverlap = 'Overlap(Covered)' 

    def setBabyCovered(self):
        if self.covered.get() == '0':
            self.infoCovered = 'No blanket'
        else:
            self.infoCovered = 'In blanket'

    # [Load Image]
    def selectSrcDir(self):
        path = filedialog.askdirectory(title="Select image source folder", initialdir=self.svSourcePath.get())
        self.svSourcePath.set(path)
        self.loadUnLabelImg()
        return

    def selectLoadDir(self):
        path = filedialog.askdirectory(title="Select image source folder", initialdir=self.svLoadPath.get())
        self.svLoadPath.set(path)
        self.loadLabeledImg()
        return

    def loadUnLabelImg(self):
        self.loadLabelOnly = 0
        self.parent.focus()
        self.imageDir = self.svSourcePath.get()
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
            print('No images found in the specified dir!')
            return

        # count total before deduction done list
        self.cur = 1
        self.count = 1
        self.total = len(self.imageList)
        self.imageList.sort()

        # set up output label dir the same as svSourcePath
        self.outDir = self.svSourcePath.get() + '/Labels'
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
        print('%d images loaded from %s, still %s undone' %(self.total, self.imageDir, self.undone))

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
        self.loadLabel()
        self.previewImageLabelGUI()

    def loadImage(self):
        # load image & directory information
        # save 4 items: image path, colored, scene, pet
        imagepath = self.imageList[self.cur - 1]
        self.imgInfo.append(imagepath)

        if platform.system() == 'Windows':
            rawinfo = imagepath.split('/')[-1]
            nextlevel = rawinfo.split('\\')
            basicinfo = nextlevel[0].split('_')
        else:
            basicinfo = imagepath.split('/')[-2].split('_')

        for (i, text) in enumerate(basicinfo):
            if text == 'bw':
                self.imgInfo.append(0)
            elif text == 'colored':
                self.imgInfo.append(1)
            elif text == 'crib':
                self.imgInfo.append('crib')
            elif text == 'bedroom':
                self.imgInfo.append('bedroom')
            elif text == 'livingroom':
                self.imgInfo.append('livingroom')
            elif text == 'nopet':
                self.imgInfo.append(0)
            elif text == 'pet':
                self.imgInfo.append(1)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        max_width = screen_width * 0.6
        max_height = screen_height * 0.6
        rawimg = Image.open(imagepath)
        self.img =ImageEnhance.Brightness(rawimg).enhance(1.2)

        size = self.img.size
        long_side = 800

        #if (size[0] and size[1]) < long_side:
        if size[0] >= size[1]:
            self.factor = long_side / size[0]
            self.img = self.img.resize((800, int(size[1]*self.factor)))
        else:
            self.factor = long_side / size[1]
            self.img = self.img.resize((int(size[0]*self.factor), 800))
        print('Resize factor = ', self.factor, ' Original size = ', size, ' Current size = ', self.img.size)
        '''
        else:
            if size[0] >= size[1]:
                self.factor = long_side * size[0]
                self.img = self.img.resize((800, int(size[1]*self.factor)))
            else:
                self.factor = long_side * size[1]
                self.img = self.img.resize((int(size[0]*self.factor), 800))
        '''
        #self.factor = min(round(max_width/size[0], 2), round(max_height/size[1], 2))
        #self.img = self.img.resize((int(size[0]*self.factor), int(size[1]*self.factor)))
        
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), PSIZE), height = max(self.tkimg.height(), PSIZE))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

        if self.loadLabelOnly == 1:
            self.progLabel.config(text = "%04d/%04d" %(self.cur, len(self.imageList)))
        else:
            self.progLabel.config(text = "%04d/%04d" %(self.cur, self.undone))
        self.area = self.tkimg.width() * self.tkimg.height()
        self.imagename, _ = os.path.splitext(os.path.basename(imagepath))
        self.filenameLabel.config(text = "File name : %s" %(self.imagename))
        self.clearBBox()

    def loadLabel(self):
        imagepath = self.imageList[self.cur - 1]
        fullfilename = os.path.basename(imagepath)
        self.imagename, _ = os.path.splitext(fullfilename)
        self.filenameLabel.config(text = "File name : %s" %(self.imagename))

        LabelFile = self.svLoadPath.get() + '/Labels/' + self.imagename + '.json'
        bbox_cnt = 0
        tmp = [0,0,0,0, '']
        with open(LabelFile, 'r') as f:
            data = json.load(f)
            if 'bbox' not in data[self.imagename].keys():
                self.mainPanel.create_text(300, 400, font=("Arial", 18), fill='black', text="No Object image. Skip")
                return

            bbox_cnt = len(data[self.imagename]['bbox'])
            for i in range(bbox_cnt):
                tmp[0] = data[self.imagename]['bbox'][i]['x1']
                tmp[1] = data[self.imagename]['bbox'][i]['y1']
                tmp[2] = data[self.imagename]['bbox'][i]['x2']
                tmp[3] = data[self.imagename]['bbox'][i]['y2']
                tmp[4] = data[self.imagename]['bbox'][i]['class']

                tmp[0] = int(int(tmp[0])*self.factor)
                tmp[1] = int(int(tmp[1])*self.factor)
                tmp[2] = int(int(tmp[2])*self.factor)
                tmp[3] = int(int(tmp[3])*self.factor)
                self.bboxList.append(tuple(tmp))
                color_index = (len(self.bboxList)-1) % len(COLORS)
                tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                        tmp[2], tmp[3], \
                                                        width = 2, \
                                                        outline = COLORS[color_index])
                classId = self.mainPanel.create_text(tmp[0] + 40, tmp[1] + 10, font=("Arial", 14), fill=COLORS[color_index], text=tmp[4])
                self.classIdList.append(classId)
                self.bboxIdList.append(tmpId)
                self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(tmp[0], tmp[1], tmp[2], tmp[3]))
                self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[color_index])

    def prevImage(self, event = None):
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()
            self.loadLabel()

    def nextImage(self, event = None):
        if self.cur < len(self.imageList):
            self.cur += 1
            self.loadImage()
            self.loadLabel()

    def deleteLabel(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        for idx in range(len(self.classIdList)):
            self.mainPanel.delete(self.classIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        pointx = int(root.winfo_screenwidth() * 0.6 * 0.5) - 50
        pointy = int(root.winfo_screenheight() * 0.6 * 0.5)
        self.mainPanel.create_text(pointx, pointy, font=("Arial", 40), fill='blue', text="Label has been deleted!!")
        LabelFile = self.svLoadPath.get() + '/Labels/' + self.imagename + '.json'
        os.remove(LabelFile)
        print('Image No. %s Label has been deleted.' %(self.imagename))

    def mouseClick(self, event):
        boxWidth = 0
        boxHeight = 0

        if self.loadLabelOnly == 1:
            return
        if self.STATE['click'] == 0:
            if self.childBtn['state'] == 'normal':
                return
            self.STATE['x'], self.STATE['y'] = event.x, event.y
            self.initStateGUI()
        else:
            self.enableBottomGUI()
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
            self.bboxBtn.config(state=NORMAL)
            self.enableControlGUI()

            if (x2 - x1) > 0:
                boxWidth = x2 - x1
            else:
                boxWidth = x1 - x2

            if (y2 - y1) > 0:
                boxHeight = y2 - y1
            else:
                boxHeight = y1 - y2
            bbox_area = boxWidth * boxHeight
            percentage = float(bbox_area / self.area) * 100

            if percentage < 20:
                self.sizeList.append('small')
            elif 20 <= percentage < 50:
                self.sizeList.append('middle')
            else:
                self.sizeList.append('large')
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            COLOR_INDEX = len(self.bboxIdList) % len(COLORS)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[len(self.bboxList) % len(COLORS)])

    def confirmBBOX(self):
        if self.classname.get() =='None' or self.ages.get() =='None' or len(self.bboxIdList) == 0:
            return
        self.popupWindowGen(popupWindowType='BBOX_OK')

    def confirmPhoto(self):
        if self.classname.get()=='None' or self.ages.get()=='None':
            return
        self.popupWindowGen(popupWindowType='DONE')

    def confirmNoObjPhoto(self):
        self.popupWindowGen(popupWindowType='NO_OBJ')

    # create pop-up window
    def popupWindowGen(self, popupWindowType=None):
        self.disableAllGUI()

        self.WindwType = popupWindowType
        if self.WindwType == 'BBOX_OK':
            self.appendToList()
            self.popupWindow = Toplevel(self.parent)
            self.popupWindow.geometry("%dx%d+%d+%d" % (300, 300, 200, 500))
            self.popupWindow.title("Sure?")

            textOne = self.handleBodyPosture()
            textTwo = self.handleBodyCovered()
            self.bboxInfoOne = Label(self.popupWindow, bg='tomato', width=24, height = 3)
            self.bboxInfoOne.config(text = self.infoClass + '/' + self.infoAge, font=("Courier", 18), fg='white')
            self.bboxInfoOne.grid(row = 0, column = 0, sticky = N+S+W+E)
            self.bboxInfoTwo = Label(self.popupWindow, bg='tomato', width=24, height = 3)
            self.bboxInfoTwo.config(text = textOne, font=("Courier", 18), fg='white')
            self.bboxInfoTwo.grid(row = 1, column = 0, sticky = N+S+W+E)
            self.bboxInfoThr = Label(self.popupWindow, bg='tomato', width=24, height = 3)
            self.bboxInfoThr.config(text = textTwo, font=("Courier", 18), fg='white')
            self.bboxInfoThr.grid(row = 2, column = 0, sticky = N+S+W+E)
            self.btn_popup1 = Button(self.popupWindow, text="OK", height=3, command=self.popup_ok)
            self.btn_popup1.grid(row = 3, column = 0, sticky = N+S+W+E)
            self.btn_popup2 = Button(self.popupWindow, text="CANCEL", height=3, command=self.popup_cancel)
            self.btn_popup2.grid(row = 4, column = 0, sticky = N+S+W+E)

        elif self.WindwType == 'DONE':
            self.popupWindow = Toplevel(self.parent)
            self.popupWindow.title("Sure?")
            self.popup_label = Label(self.popupWindow,text="Save and load next image", font=("Courier", 18), fg="black")
            self.popupWindow.geometry("%dx%d+%d+%d" % (300, 200, 200, 500))
            self.popup_label.pack()
            self.btn_popup1 = Button(self.popupWindow, text="OK", width=20, height=3, command=self.popup_ok)
            self.btn_popup1.pack(side=RIGHT)
            self.btn_popup2 = Button(self.popupWindow, text="CANCEL", width=20, height=3, command=self.popup_cancel)
            self.btn_popup2.pack(side=LEFT)

        elif self.WindwType == 'NO_OBJ':
            self.popupWindow = Toplevel(self.parent)
            self.popupWindow.title("Sure?")
            self.bboxInfoOne = Label(self.popupWindow, bg='tomato', width=20, height = 3, text='')
            self.bboxInfoOne.grid(row = 0, column = 0, sticky = W+E)
            self.bboxInfoOne.config(text = "NO Objects?", font=("Courier", 20), fg='white')
            self.btn_popup1 = Button(self.popupWindow, text="OK", height=2, width=5, command=self.popup_ok)
            self.btn_popup2 = Button(self.popupWindow, text="CANCEL", height=2, width=5, command=self.popup_cancel)
            self.btn_popup1.grid(row = 3, column = 1, sticky = W+E)
            self.btn_popup2.grid(row = 3, column = 0, sticky = W+E)

        else:
            messagebox.showerror("Error!", message = "popup window error!")

    def popup_ok(self):
        self.popupWindow.destroy()
        if self.WindwType == 'BBOX_OK':
            self.resetBtnValue()
            self.disableBottomGUI()
            self.enableControlGUI()
        else:
            self.noObjBtn.config(state=NORMAL)
            self.updateImageDic()

    def popup_cancel(self):
        self.popupWindow.destroy()
        self.enableBottomGUI()
        self.enableControlGUI()
        if self.WindwType == 'BBOX_OK':
            self.popLastList()
            self.bboxBtn.config(state=NORMAL)

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        self.disableBottomGUI()
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)
        self.sizeList.pop(idx)

        # when index is 0, all List length should be 1
        if (idx + 1) == len(self.classList):
            self.popLastList()

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.classList = []
        self.ageList = []
        self.leanList = []
        self.twistList = []
        self.blanketList = []
        self.overlapList = []
        self.sizeList = []
        if self.loadLabelOnly == 1:
            self.previewImageLabelGUI()
        else:
            self.initStateGUI()

    def handleBodyPosture(self):
        textOne = self.infoBodyLean.split('No')[0] + ' / ' + self.infoBodyTwisted.split('No')[0]
        return textOne
    def handleBodyCovered(self):
        textTwo = self.infoCovered.split('No')[0] + ' / ' + self.infoBodyOverlap.split('No')[0]
        return textTwo

    def appendToList(self):
        self.classList.append(self.infoClass)
        self.ageList.append(self.infoAge)
        self.leanList.append(self.infoBodyLean)
        self.twistList.append(self.infoBodyTwisted)
        self.blanketList.append(self.infoCovered)
        self.overlapList.append(self.infoBodyOverlap)

    def popLastList(self):
        self.classList = self.classList[:-1]
        self.ageList = self.ageList[:-1]
        self.leanList = self.leanList[:-1]
        self.twistList = self.twistList[:-1]
        self.blanketList = self.blanketList[:-1]
        self.overlapList = self.overlapList[:-1]

    def printAllList(self):
        print(self.imgInfo)
        print(self.bboxList)
        print(self.classList)
        print(self.ageList)
        print(self.leanList)
        print(self.twistList)
        print(self.blanketList)
        print(self.overlapList)
        print(self.sizeList)


    #[Ryk] ToDo
    def updateImageDic(self):
        print (">>>> updateImageDic")
        img_dict = {}
        data = {}
        num_child = 0
        for i in range(len(self.classList)):
            if self.classList[i] == 'Child':
                num_child += 1
        num_adult = len(self.classList) - num_child

        data['path'] = self.imgInfo[0]
        data['num_child'] = num_child
        data['num_adult'] = num_adult
        data['colored'] = self.imgInfo[1]
        data['scene'] = self.imgInfo[2]
        data['pet'] = self.imgInfo[3]

        if len(self.bboxList) > 0:
            data['bbox'] = []
            for i, point in enumerate(self.bboxList):
                data['bbox'].append({
                    'id': i,
                    'x1': int(point[0] / self.factor),
                    'y1': int(point[1] / self.factor) ,
                    "x2": int(point[2] / self.factor),
                    "y2": int(point[3] / self.factor),
                    "class": self.classList[i],
                    "age_range": self.ageList[i],
                    "blanket": self.blanketList[i],
                    "size": self.sizeList[i]
                })

        img_dict[self.imagename] = data
        self.labelfilename = self.outDir + '/' + self.imagename +  '.json'
        with open(self.labelfilename, 'w') as outfile:
            json.dump(img_dict, outfile, indent = 4)
        print('Image No. %d saved' %(self.cur))
        print ('cur:', self.cur, 'count: ', self.count, 'undone: ', self.undone)

        self.imgInfo = []
        self.cur += 1
        self.count += 1
        if self.count <= self.undone:
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
