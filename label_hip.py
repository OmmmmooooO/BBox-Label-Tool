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
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # reference to whole image information
        # sve path, colored, scene, pet
        self.imgInfo = []
        self.infoClass = ''
        self.infoAge = ''
        self.infoFace = ''
        self.infoCovered = ''

        # reference to bbox info
        self.classList = []
        self.ageList = []
        self.blanketList = []
        self.faceList =[]
        self.sizeList = []

        # ----------------- GUI stuff ---------------------
        # [UPPER PART]
        ## button: Image Folder
        self.srcDirBtn = Button(self.frame, text = "Image Folder", command = self.selectSrcDir, width = 10)
        self.srcDirBtn.grid(row = 0, column = 0)

        ## entry: input image dir
        self.svSourcePath = StringVar()
        self.svSourcePath.set(os.getcwd())
        self.entrySrc = Entry(self.frame, textvariable = self.svSourcePath)
        self.entrySrc.grid(row = 0, column = 1, columnspan=4, sticky = W+E)

        # [CENTRE PART]
        ## main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor = 'tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        #self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("c", self.cancelBBox)
        # self.parent.bind("p", self.prevImage) # press 'p' to go backforward
        # self.parent.bind("n", self.nextImage) # press 'n' to go forward
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, columnspan = 4, sticky = W+E+N+S)

        ## radio button: Class
        self.classLb = Label(self.frame, text = 'Class:')
        self.classLb.grid(row = 7, column = 1, padx = (0,60), sticky = N+E)
        self.classname = StringVar()
        self.classname.set(None)
        self.childBtn = Radiobutton(self.frame, text='Child', variable=self.classname, value='0', command = self.setClass, state = DISABLED)
        self.childBtn.grid(row = 8, column = 1, padx = (0,50), sticky = N+E)
        self.adultBtn = Radiobutton(self.frame, text='Adult', variable=self.classname, value='1', command = self.setClass, state = DISABLED)
        self.adultBtn.grid(row = 9, column = 1, padx = (0,50), sticky = N+E)

        ## radio button: Age
        self.ageLb = Label(self.frame, text = 'Age:')
        self.ageLb.grid(row = 7, column = 2, sticky = N+W)
        self.ages = StringVar()
        self.ages.set(None)
        self.age6mBtn = Radiobutton(self.frame, text='0-6 month', variable=self.ages, value='0', command = self.setAge, state = DISABLED)
        self.age6mBtn.grid(row = 8, column = 2, padx = (0,50), sticky = N+W)
        self.age12mBtn = Radiobutton(self.frame, text='7-12 month', variable=self.ages, value='1', command = self.setAge, state = DISABLED)
        self.age12mBtn.grid(row = 9, column = 2, padx = (0,50), sticky = N+W)
        self.age6yrBtn = Radiobutton(self.frame, text='12m-6 years', variable=self.ages, value='2', command = self.setAge, state = DISABLED)
        self.age6yrBtn.grid(row = 10, column = 2, padx = (0,50), sticky = N+W)
        self.age6upBtn = Radiobutton(self.frame, text='6 years up', variable=self.ages, value='3', command = self.setAge, state = DISABLED)
        self.age6upBtn.grid(row = 11, column = 2, padx = (0,50), sticky = N+W)

        ## radio button: Face direction
        self.fcLb = Label(self.frame, text = 'Face direction:')
        self.fcLb.grid(row = 7, column = 3, padx = (0,40), sticky = N+W)
        self.facedir = StringVar()
        self.facedir.set(None)
        self.fcfrontBtn = Radiobutton(self.frame, text='Front', variable=self.facedir, value='0', command = self.setFace, state = DISABLED)
        self.fcfrontBtn.grid(row = 8, column = 3, padx = (0,50), sticky = N+W)
        self.fcsideBtn = Radiobutton(self.frame, text='Side', variable=self.facedir, value='1', command = self.setFace, state = DISABLED)
        self.fcsideBtn.grid(row = 9, column = 3, padx = (0,50), sticky = N+W)
        self.fcbackBtn = Radiobutton(self.frame, text='Back', variable=self.facedir, value='2', command = self.setFace, state = DISABLED)
        self.fcbackBtn.grid(row = 10, column = 3, padx = (0,50), sticky = N+W)

        ## check button: In blanket
        self.covered = StringVar()
        self.covered.set(None)
        self.coveredBtn = Checkbutton(self.frame, text='In blanket', variable=self.covered, onvalue=1, offvalue=0, command = self.setCovered, state = DISABLED)
        self.coveredBtn.grid(row = 7, column = 4, padx = (0,50), sticky = N+E)

        ## control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 12, column = 1, columnspan = 4, sticky = W+E)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.filenameLabel = Label(self.ctrPanel, text = "File name:")
        self.filenameLabel.pack(side = LEFT, padx = 5)

        # [RIGHT PART]
        ## showing bbox info & delete bbox
        self.BtnPanel = Frame(self.frame)
        self.BtnPanel.grid(row = 1, column = 5, sticky = W+E+N+S)
        self.lb1 = Label(self.BtnPanel, text = 'Bounding boxes:')
        self.lb1.pack()
        self.btnDel = Button(self.BtnPanel, text = 'Delete', width = 20, height = 2, command = self.delBBox, state = DISABLED)
        self.btnDel.pack()
        self.btnClear = Button(self.BtnPanel, text = 'ClearAll', width = 20, height = 2, command = self.clearBBox, state = DISABLED)
        self.btnClear.pack()
        self.listbox = Listbox(self.BtnPanel, width = 25, height = 25)
        self.listbox.pack()
        self.noObjBtn = Button(self.BtnPanel, text = 'NO Objects', width = 20, height = 3, command = self.confirmNoObjPhoto)
        self.noObjBtn.pack()
        self.bboxBtn = Button(self.BtnPanel, text = 'BBOX OK', width = 20, height = 3, command = self.confirmBBOX, state = DISABLED)
        self.bboxBtn.pack()
        self.doneBtn = Button(self.BtnPanel, text = 'Image DONE', width = 20, height = 3, command = self.confirmPhoto, fg='red', state = DISABLED)
        self.doneBtn.pack()

         # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

    def selectSrcDir(self):
        path = filedialog.askdirectory(title="Select image source folder", initialdir=self.svSourcePath.get())
        self.svSourcePath.set(path)
        self.loadDir()
        return

    def enableGUI(self):
        self.childBtn.config(state=NORMAL)
        self.adultBtn.config(state=NORMAL)
        self.age6mBtn.config(state=NORMAL)
        self.age12mBtn.config(state=NORMAL)
        self.age6yrBtn.config(state=NORMAL)
        self.age6upBtn.config(state=NORMAL)
        self.fcfrontBtn.config(state=NORMAL)
        self.fcsideBtn.config(state=NORMAL)
        self.fcbackBtn.config(state=NORMAL)
        self.coveredBtn.config(state=NORMAL)
        self.btnDel.config(state=NORMAL)
        self.btnClear.config(state=NORMAL)
        self.bboxBtn.config(state=NORMAL)
        self.doneBtn.config(state=NORMAL)

    def disableGUI(self):
        self.childBtn.config(state=DISABLED)
        self.adultBtn.config(state=DISABLED)
        self.age6mBtn.config(state=DISABLED)
        self.age12mBtn.config(state=DISABLED)
        self.age6yrBtn.config(state=DISABLED)
        self.age6upBtn.config(state=DISABLED)
        self.fcfrontBtn.config(state=DISABLED)
        self.fcsideBtn.config(state=DISABLED)
        self.fcbackBtn.config(state=DISABLED)
        self.coveredBtn.config(state=DISABLED)
        self.btnDel.config(state=DISABLED)
        self.btnClear.config(state=DISABLED)
        self.bboxBtn.config(state=DISABLED)
        self.doneBtn.config(state=DISABLED)

    def enableBottomGUI(self):
        self.childBtn.config(state=NORMAL)
        self.adultBtn.config(state=NORMAL)
        self.age6mBtn.config(state=NORMAL)
        self.age12mBtn.config(state=NORMAL)
        self.age6yrBtn.config(state=NORMAL)
        self.age6upBtn.config(state=NORMAL)
        self.fcfrontBtn.config(state=NORMAL)
        self.fcsideBtn.config(state=NORMAL)
        self.fcbackBtn.config(state=NORMAL)
        self.coveredBtn.config(state=NORMAL)

    def disableBottomGUI(self):
        self.childBtn.config(state=DISABLED)
        self.adultBtn.config(state=DISABLED)
        self.age6mBtn.config(state=DISABLED)
        self.age12mBtn.config(state=DISABLED)
        self.age6yrBtn.config(state=DISABLED)
        self.age6upBtn.config(state=DISABLED)
        self.fcfrontBtn.config(state=DISABLED)
        self.fcsideBtn.config(state=DISABLED)
        self.fcbackBtn.config(state=DISABLED)
        self.coveredBtn.config(state=DISABLED)

    def setClass(self):
        if self.classname.get() == '0':
            self.infoClass = 'Child'
        else:
            self.infoClass = 'Adult'
        print('set class:', self.classname.get(), ' is ', self.infoClass)

    def setAge(self):
        if self.ages.get() == '0':
            self.infoAge = '0-6 month'
        elif self.ages.get() == '1':
            self.infoAge = '7-12 month'
        elif self.ages.get() == '2':
            self.infoAge = '1-6 years old'
        else:
            self.infoAge = '6 years up'
        print('set age:', self.ages.get(), ' is ', self.infoAge)

    def setFace(self):
        if self.facedir.get() == '0':
            self.infoFace = 'Front'
        elif self.facedir.get() == '1':
            self.infoFace = 'Side'
        else:
            self.infoFace = 'Back'
        print('set face direction:', self.facedir.get(), ' is ', self.infoFace)

    def setCovered(self):
        if self.covered.get() == '0':
            self.infoCovered = 'No blanket'
        else:
            self.infoCovered = 'In blanket'
        print('set covered:', self.covered.get(), ' is ', self.infoCovered)

    def loadDir(self):
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
            print(type(self.imageList),type(filelist))

        if len(self.imageList) == 0:
            print('No images found in the specified dir!')
            return

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
            #self.loadLabel()
        print('%d images loaded from %s, still %s undone' %(self.total, self.imageDir, self.undone))

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
        max_width = screen_width * 0.7
        max_height = screen_height * 0.7
        self.img = Image.open(imagepath)
        size = self.img.size
        self.factor = 1
        if (size[0] or size[1]) < 800:
            pass
        else:
            if size[0] >= size[1]:
                self.factor = 800 / size[0]
                self.img = self.img.resize((800, int(size[1]*self.factor)))
            else:
                self.factor = 800 / size[1]
                self.img = self.img.resize((int(size[0]*self.factor), 800))

        #self.factor = min(round(max_width/size[0], 2), round(max_height/size[1], 2))
        #self.img = self.img.resize((int(size[0]*self.factor), int(size[1]*self.factor)))
        print ("Image fator: ", self.factor , " resize to: ",  (self.img.size[0], self.img.size[1]))

        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), PSIZE), height = max(self.tkimg.height(), PSIZE))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.undone))
        self.area = self.tkimg.width() * self.tkimg.height()
        self.imagename, _ = os.path.splitext(os.path.basename(imagepath))
        self.filenameLabel.config(text = "File name : %s" %(self.imagename))
        self.clearBBox()
        print(self.imgInfo)

    # [NOT USE]
    def loadLabel(self):
        imagepath = self.imageList[self.cur - 1]
        fullfilename = os.path.basename(imagepath)
        self.imagename, _ = os.path.splitext(fullfilename)
        self.filenameLabel.config(text = "File name : %s" %(self.imagename))
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    tmp = [int(t.strip()) for t in line.split()]
                    tmp = line.split()
                    tmp[0] = int(int(tmp[0])/self.factor)
                    tmp[1] = int(int(tmp[1])/self.factor)
                    tmp[2] = int(int(tmp[2])/self.factor)
                    tmp[3] = int(int(tmp[3])/self.factor)
                    self.bboxList.append(tuple(tmp))
                    color_index = (len(self.bboxList)-1) % len(COLORS)
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[2], tmp[3], \
                                                            width = 2, \
                                                            outline = COLORS[color_index])
                                                            #outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(tmp[0], tmp[1], tmp[2], tmp[3]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[color_index])
                    #self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    # [NOT USE]
    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    # [NOT USE]
    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.undone:
            self.cur += 1
            self.loadImage()

    # [NOT USE]
    def saveImage(self):
        if self.labelfilename == '':
            return
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.bboxList))
            for bbox in self.bboxList:
                f.write("{} {} {} {} {}\n".format(int(int(bbox[0])*self.factor),
                                                int(int(bbox[1])*self.factor),
                                                int(int(bbox[2])*self.factor),
                                                int(int(bbox[3])*self.factor), bbox[4]))
        print('Image No. %d saved' %(self.cur))

    def mouseClick(self, event):
        boxWidth = 0
        boxHeight = 0
        if self.STATE['click'] == 0:
            if self.childBtn['state'] == 'normal':
                return
            self.STATE['x'], self.STATE['y'] = event.x, event.y
            self.disableGUI()
        else:
            self.enableBottomGUI()
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
            self.enableGUI()

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
        if self.classname.get()=='None' or self.ages.get()=='None' or self.facedir.get()=='None' or len(self.bboxIdList) == 0:
            return
        if self.classname.get() == '1' and self.ages.get() != '3':
            self.popupWindowGen(popupWindowType='AGE')
            return
        if self.covered.get() == 'None': #prevent initial no value'
            self.infoCovered = 'No blanket'
        self.popupWindowGen(popupWindowType='BBOX_OK')

    def confirmPhoto(self):
        if self.classname.get()=='None' or self.ages.get()=='None' or self.facedir.get()=='None':
            return
        self.popupWindowGen(popupWindowType='DONE')

    def confirmNoObjPhoto(self):
        self.popupWindowGen(popupWindowType='NO_OBJ')

    # create pop-up window
    def popupWindowGen(self, popupWindowType=None, okBtn=True):
        self.popupWindowFlag = 1

        self.WindwType = popupWindowType
        if self.WindwType == 'BBOX_OK':
            self.bboxBtn.config(state=DISABLED)
            self.popupWindow = Toplevel(self.parent)
            self.popupWindow.title("Sure?")

            self.bboxInfoOne = Label(self.popupWindow, bg='tomato', width=20, height = 3, text='')
            self.bboxInfoOne.grid(row = 0, column = 0, sticky = W+E)
            self.bboxInfoOne.config(text = self.infoClass + '/' + self.infoAge, font=("Courier", 20), fg='white')
            self.bboxInfoTwo = Label(self.popupWindow, bg='tomato', width=20, height = 3, text='')
            self.bboxInfoTwo.grid(row = 1, column = 0, sticky = W+E)
            self.bboxInfoTwo.config(text = self.infoFace + '/' + self.infoCovered, font=("Courier", 20), fg='white')
            self.popup_label = Label(self.popupWindow, text="Confirmed & Label next bbox?", font=("Courier", 15), fg="black")
            self.popup_label.grid(row = 2, column = 0, sticky = W+E)

            self.btn_popup1 = Button(self.popupWindow, text="OK", height=2, width=5, command=self.popup_ok)
            self.btn_popup2 = Button(self.popupWindow, text="CANCLE", height=2, width=5, command=self.popup_cancle)
            self.btn_popup1.grid(row = 3, column = 1, sticky = W+E)
            self.btn_popup2.grid(row = 3, column = 0, sticky = W+E)
            if okBtn == False:
                self.btn_popup1.config(state=DISABLED)

        elif self.WindwType == 'DONE':
            self.doneBtn.config(state=DISABLED)
            self.popupWindow = Toplevel(self.parent)
            self.popupWindow.title("Sure?")
            self.popup_label = Label(self.popupWindow,text="Save and load next image", fg="black")
            self.popupWindow.geometry("%dx%d" % (400, 200))
            self.popup_label.pack()
            self.btn_popup1 = Button(self.popupWindow, text="OK", height=2, width=5, command=self.popup_ok)
            self.btn_popup2 = Button(self.popupWindow, text="CANCLE", height=2, width=5, command=self.popup_cancle)
            self.btn_popup1.pack(side=RIGHT)
            self.btn_popup2.pack(side=LEFT)
            if okBtn == False:
                self.btn_popup1.config(state=DISABLED)

        elif self.WindwType == 'NO_OBJ':
            self.noObjBtn.config(state=DISABLED)
            self.popupWindow = Toplevel(self.parent)
            self.popupWindow.title("Sure?")
            self.bboxInfoOne = Label(self.popupWindow, bg='tomato', width=20, height = 3, text='')
            self.bboxInfoOne.grid(row = 0, column = 0, sticky = W+E)
            self.bboxInfoOne.config(text = "NO Objects?", font=("Courier", 20), fg='white')
            self.btn_popup1 = Button(self.popupWindow, text="OK", height=2, width=5, command=self.popup_ok)
            self.btn_popup2 = Button(self.popupWindow, text="CANCLE", height=2, width=5, command=self.popup_cancle)
            self.btn_popup1.grid(row = 3, column = 1, sticky = W+E)
            self.btn_popup2.grid(row = 3, column = 0, sticky = W+E)

        elif self.WindwType == 'AGE':
            messagebox.showerror("Error!", message = "Age error!")

        else:
            messagebox.showerror("Error!", message = "popup window error!")

    def popup_ok(self):
        self.popupWindow.destroy()
        self.popupWindowFlag = 0
        self.disableBottomGUI()

        if self.WindwType == 'BBOX_OK':
            self.updateBBoxList()
        else:
            self.noObjBtn.config(state=NORMAL)
            self.updateImageDic()

    def popup_cancle(self):
        self.popupWindow.destroy()
        self.popupWindowFlag = 0

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        # delete bbox only
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

        # delete bbox detail
        self.classList.pop(idx)
        self.ageList.pop(idx)
        self.blanketList.pop(idx)
        self.faceList.pop(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.classList = []
        self.ageList = []
        self.blanketList = []
        self.faceList = []
        self.sizeList = []
        self.disableGUI()

    def updateBBoxList(self):
        print (">>>> updateBBoxList")
        self.classList.append(self.infoClass)
        self.ageList.append(self.infoAge)
        self.faceList.append(self.infoFace)
        self.blanketList.append(self.infoCovered)

        if (len(self.bboxList)>1) and (self.bboxList[-1]==self.bboxList[-2]):
            self.mainPanel.delete(self.bboxIdList[-1])
            self.bboxIdList.pop(-1)
            self.bboxList.pop(-1)
            self.listbox.delete(-1)
            self.sizeList.pop(-1)

            # delete bbox detail
            self.classList.pop(-1)
            self.ageList.pop(-1)
            self.blanketList.pop(-1)
            self.faceList.pop(-1)

        #e.g. draw a bbox -> Delete -> BBOX OK
        if len(self.bboxList)!=len(self.classList):
            # delete bbox detail
            self.classList.pop(-1)
            self.ageList.pop(-1)
            self.blanketList.pop(-1)
            self.faceList.pop(-1)

        # debug
        print(self.imgInfo)
        print(self.bboxList)
        print(self.classList)
        print(self.ageList)
        print(self.faceList)
        print(self.blanketList)
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
                    "face": self.faceList[i],
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