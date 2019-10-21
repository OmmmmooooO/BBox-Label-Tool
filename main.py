from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import Toplevel
from PIL import Image, ImageTk
import os
import glob
import json
import random
import utils

# colors for the bboxes
COLORS = ['cyan', 'blue', 'red', 'orange', 'limegreen', 'hotpink', 'green', 'fuchsia',  'olive', 'darkviolet']
# image sizes for the examples
SIZE = 256, 256
# panel size for init
PSIZE = 400
# label.json
LABEL_JSON = 'label.json'


class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.currentLabelclass = ''
        self.cla_can_temp = []
        self.classcandidate_filename = 'class.txt'

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
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("p", self.prevImage) # press 'p' to go backforward
        self.parent.bind("n", self.nextImage) # press 'n' to go forward 
        self.mainPanel.grid(row = 2, column = 1, rowspan = 4, columnspan = 4, sticky = W+E+N+S)

        ## radio button: Class
        self.classLb = Label(self.frame, text = 'Class:')
        self.classLb.grid(row = 6, column = 1, padx = (0,60), sticky = N+E)
        self.classname = StringVar()
        self.classname.set(None)
        self.childBtn = Radiobutton(self.frame, text='Child', variable=self.classname, value='0', command = self.setClass, state = DISABLED)
        self.childBtn.grid(row = 7, column = 1, padx = (0,50), sticky = N+E)
        self.adultBtn = Radiobutton(self.frame, text='Adult', variable=self.classname, value='1', command = self.setClass, state = DISABLED)
        self.adultBtn.grid(row = 8, column = 1, padx = (0,50), sticky = N+E)

        ## radio button: Age
        self.ageLb = Label(self.frame, text = 'Age:')
        self.ageLb.grid(row = 6, column = 2, sticky = N+W)
        self.ages = StringVar()
        self.ages.set(None)
        self.age6mBtn = Radiobutton(self.frame, text='0-6 month', variable=self.ages, value='0', command = self.setAge, state = DISABLED)
        self.age6mBtn.grid(row = 7, column = 2, padx = (0,50), sticky = N+W)
        self.age12mBtn = Radiobutton(self.frame, text='7-12 month', variable=self.ages, value='1', command = self.setAge, state = DISABLED)
        self.age12mBtn.grid(row = 8, column = 2, padx = (0,50), sticky = N+W)
        self.age6yrBtn = Radiobutton(self.frame, text='12m-6 years', variable=self.ages, value='2', command = self.setAge, state = DISABLED)
        self.age6yrBtn.grid(row = 9, column = 2, padx = (0,50), sticky = N+W)
        self.age6upBtn = Radiobutton(self.frame, text='6 years up', variable=self.ages, value='3', command = self.setAge, state = DISABLED)
        self.age6upBtn.grid(row = 10, column = 2, padx = (0,50), sticky = N+W)
        
        ## radio button: Face direction
        self.fcLb = Label(self.frame, text = 'Face direction:')
        self.fcLb.grid(row = 6, column = 3, padx = (0,40), sticky = N+W)
        self.facedir = StringVar()
        self.facedir.set(None)
        self.fcfrontBtn = Radiobutton(self.frame, text='Front', variable=self.facedir, value='0', command = self.setFace, state = DISABLED)
        self.fcfrontBtn.grid(row = 7, column = 3, padx = (0,50), sticky = N+W)
        self.fcsideBtn = Radiobutton(self.frame, text='Side', variable=self.facedir, value='1', command = self.setFace, state = DISABLED)
        self.fcsideBtn.grid(row = 8, column = 3, padx = (0,50), sticky = N+W)
        self.fcbackBtn = Radiobutton(self.frame, text='Back', variable=self.facedir, value='2', command = self.setFace, state = DISABLED)
        self.fcbackBtn.grid(row = 9, column = 3, padx = (0,50), sticky = N+W)

        ## check button: In blanket
        self.covered = StringVar()
        self.covered.set(None)
        self.coveredBtn = Checkbutton(self.frame, text='In blanket', variable=self.covered, onvalue=1, offvalue=0, command = self.setCovered, state = DISABLED)
        self.coveredBtn.grid(row = 6, column = 4, padx = (0,50), sticky = N+E)
       
        ## control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 11, column = 1, columnspan = 4, sticky = W+E)
        '''
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        '''
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)

        self.filenameLabel = Label(self.ctrPanel, text = "File name:")
        self.filenameLabel.pack(side = LEFT, padx = 5)
        '''
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)
        '''

        # [RIGHT PART]
        ## showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 2, column = 5,  sticky = W+N)

        self.btnDel = Button(self.frame, text = 'Delete', width = 20, command = self.delBBox, state = DISABLED)
        self.btnDel.grid(row = 3, column = 5, sticky = W+N)

        self.btnClear = Button(self.frame, text = 'ClearAll', width = 20, command = self.clearBBox, state = DISABLED)
        self.btnClear.grid(row = 4, column = 5, sticky = W+N)
        
        self.listbox = Listbox(self.frame, width = 25, height = 20)
        self.listbox.grid(row = 5, column = 5, sticky = W+N)

        ## button: Bbox ok
        self.bboxBtn = Button(self.frame, text = 'BBOX OK', command = self.confirmBBOX, height = 4, state = DISABLED)
        self.bboxBtn.grid(row = 6, column = 5, rowspan = 2, sticky = W+N)

        ## button: Done and load next image
        self.doneBtn = Button(self.frame, text = 'DONE', command = self.confirmPhoto, fg='red', height = 1, state = DISABLED)
        self.doneBtn.grid(row = 9, column = 5, padx = (75, 0), sticky = W+N)

        self.logLabel_1 = Label(self.frame, bg='tomato', width=20, height = 2, text='')
        self.logLabel_1.grid(row = 10, column = 5, sticky = W+N)
        self.logLabel_2 = Label(self.frame, bg='tomato', width=20, height = 2, text='')
        self.logLabel_2.grid(row = 11, column = 5, sticky = W+N)

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

    '''
    def selectDesDir(self):
        path = filedialog.askdirectory(title="Select label output folder", initialdir=self.svDestinationPath.get())
        self.svDestinationPath.set(path)
        return
    '''

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
        self.classname.set(None)
        self.ages.set(None)
        self.facedir.set(None)
        self.covered.set(None)
        print('classname=',self.classname.get())
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

    def setAge(self):
        print('age:', self.ages.get())
        return

    def setFace(self):
        print('face direction:', self.facedir.get())

    def setCovered(self):
        print('covered:', self.covered.get())
        return

    def setClass(self):
        self.currentLabelclass = self.classname.get()
        print('set label class to : %s' % self.currentLabelclass)

    #[Ryk] ToDo
    #1. Update dictionary
    #2. Pop-up window
    def confirmBBOX(self):
        if self.classname.get() or self.ages.get() == None:
            
        textClass = self.classname.get()
        if textClass == '0':
            infoClass = 'Child'
        else:
            infoClass = 'Adult'

        textAge = self.ages.get()
        if textAge == '0':
            infoAge = '0-6 month'
        elif textAge == '1':
            infoAge = '7-12 month'
        elif textAge == '2':
            infoAge = '1-6 years old'
        else:
            infoAge = '6 years up'

        textFace = self.facedir.get()
        if textFace == '0':
            infoFace = 'Front'
        elif textFace == '1':
            infoFace = 'Side'
        else:
            infoFace = 'Back'

        textCovered = self.covered.get()
        if textCovered == '0':
            infoCovered = 'No blanket'
        else:
            infoCovered = 'In blanket'
            
        self.logLabel_1.config(text = infoClass + '/' + infoAge)
        self.logLabel_2.config(text = infoFace + '/' + infoCovered)
        self.popupWindowGen(popupWindowType = 'BBOX_OK')

    #[Ryk] ToDo
    def updateDictionary(self):
        pass
    
    #[Ryk] ToDo
    #1. Update dictionary
    #2. Save dictionary to json file
    #3. Load next image
    def confirmPhoto(self):
        self.popupWindowGen(popupWindowType = 'DONE')

    # create pop-up window
    def popupWindowGen(self, popupWindowType = None):
        self.popupWindowFlag = 1
        # BBOX OK   
        if popupWindowType == 'BBOX_OK':
            self.popupWindow = Toplevel(self.parent)
            self.popupWindow.title("Sure?")
            self.popup_label = Label(self.popupWindow,text="Label next bbox?", fg="black")
            #self.popup_label.config(width=20)
            #self.popup_label.config(font=("Courier", 14))
            self.popupWindow.geometry("%dx%d" % (400, 200))
            #self.center(self.popupWindow)
            self.popup_label.pack()
        
            self.btn_popup1 = Button(self.popupWindow, text="OK", height=1, width=5, command=self.popup_ok)
            self.btn_popup2 = Button(self.popupWindow, text="CANCLE", height=1, width=5, command=self.popup_cancle)
            self.btn_popup1.pack(side=RIGHT)
            self.btn_popup2.pack(side=LEFT)
        # DONE
        elif popupWindowType == 'DONE':          
            self.popupWindow = Toplevel(self.parent)
            self.popupWindow.title("Sure?")
            self.popup_label = Label(self.popupWindow,text="Save and load next image", fg="black")
            #self.popup_label.config(width=20)
            #self.popup_label.config(font=("Courier", 14))
            self.popupWindow.geometry("%dx%d" % (400, 200))
            #self.center(self.popupWindow)
            self.popup_label.pack()

            self.btn_popup1 = Button(self.popupWindow, text="OK", height=5, width=5, command=self.popup_ok)
            self.btn_popup2 = Button(self.popupWindow, text="CANCLE", height=5, width=5, command=self.popup_cancle)
            self.btn_popup1.pack(side=RIGHT)
            self.btn_popup2.pack(side=LEFT)
        else:
            messagebox.showerror("Error!", message = "popup window error!")


    #[Ryk] ToDo
    def popup_ok(self):
        self.popupWindow.destroy()
        self.popupWindowFlag = 0
        self.disableGUI()
        self.updateDictionary()
        '''
        if popupWindowType == 'BBOX_OK':
            #1. Save to json
            #2. Load next image
            pass    
        '''

    def popup_cancle(self):
        self.popupWindow.destroy()
        self.popupWindowFlag = 0

    def loadDir(self):
        self.parent.focus()
        self.imageDir = self.svSourcePath.get()
        self.imageList = []
        if not os.path.isdir(self.imageDir):
            messagebox.showerror("Error!", message = "The specified dir doesn't exist!")
            return

        extlist = ["*.JPEG", "*.jpeg", "*JPG", "*.jpg", "*.PNG", "*.png", "*.BMP", "*.bmp"]
        
        for e in extlist:
            filelist = glob.glob(os.path.join(self.imageDir, e))
            self.imageList.extend(filelist)
            print(type(self.imageList),type(filelist))

        if len(self.imageList) == 0:
            print('No images found in the specified dir!')
            return

        self.cur = 1
        self.total = len(self.imageList)
        self.imageList.sort()

        #[Ryk]
        #set up output dir the same as svSourcePath
        #self.outDir = os.path.join(r'./Labels', '%03d' %(self.category))
        self.outDir = self.svSourcePath.get()
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load csv file, compare images file list with csv
        undoneList = self.imageList
        if os.path.exists(self.outDir + "/" + LABEL_JSON):
            labeled_list = utils.get_image_key(self.outDir + "/" + LABEL_JSON)
            for (i, a) in enumerate(undoneList):
                for (j, n) in enumerate(undoneList):
                    name = n.split('/')[-1]
                    if a == name:
                        undoneList.remove(n)

        self.imageList = undoneList
        self.loadImage()
        print('%d images loaded from %s' %(self.total, self.imageDir))

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        print(imagepath, self.imageList)
        self.img = Image.open(imagepath)
        size = self.img.size
        self.factor = max(size[0]/1000, size[1]/1000., 1.)
        self.img = self.img.resize((int(size[0]/self.factor), int(size[1]/self.factor)))
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), PSIZE), height = max(self.tkimg.height(), PSIZE))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # load labels
        self.clearBBox()
        #self.imagename = os.path.split(imagepath)[-1].split('.')[0]
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
                    #tmp = [int(t.strip()) for t in line.split()]
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
                #f.write(' '.join(map(str, bbox)) + '\n')
        print('Image No. %d saved' %(self.cur))

    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
            self.disableGUI()
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2, self.currentLabelclass))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
            self.enableGUI()
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

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    #[Ryk] ToDo
    # if bbox == 0, then disable GUI
    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.disableGUI()

    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    '''
    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()
    '''


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
