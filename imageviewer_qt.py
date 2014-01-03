#!/usr/bin/env python

import sys
import os
import sqlite3
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

class ImageList(object):
    """A simple list of images.
    Can also load a list from a given directory, with load_dir()
    """

    valid_image_extensions = [
        '.png',
        '.jpg',
        '.jpeg',
        '.gif',
        '.bmp',
        '.svg',
        '.tif', #don't scale correctly
        '.tiff', #don't scale correctly
    ]
    pos = 0 
    imglist = None
    loop = False



    def __init__(self, array=None):
        if array:
            self.imglist = array

            
 

    def load_dir(self, directory='.'):
        # get all files in the given dir
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory,f))]

        #find only the images
        images = [
            f for f in files 
            if os.path.splitext(f)[1].lower() in self.valid_image_extensions
        ]

        if images:
            self.imglist = images

    def current(self):
        return self.imglist[self.pos]

    def next(self):
        if self.pos < (len(self.imglist) - 1):
            self.pos += 1
        else:
            if self.loop:
                self.pos = 0
            else:
                raise KeyError("No more images in the list!")

        return self.imglist[self.pos]

    def previous(self):
        if self.pos > 0:
            self.pos -= 1
        else:
            if self.loop:
                self.pos = (len(self.imglist) - 1)
            else:
                raise KeyError("No fewer images in the list!")

        return self.imglist[self.pos]

    def at_end(self):
        if self.loop:
            return False
        else:
            return self.pos >= (len(self.imglist) - 1)

    def at_beginning(self):
        if self.loop:
            return False
        else:
            return self.pos == 0
            
    def startAt(self, file_name):
        f = os.path.basename(file_name)
        for i, a in enumerate(self.imglist):
            #print a
            if a == f:
                self.pos = i

                
                
class Tag_Creation_Popup(QtGui.QLabel):

    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        
        self.setGeometry(300, 300, 300, 350)
        self.setWindowTitle('Tag Entry')
        self.setAlignment(Qt.AlignCenter) 
        self.setStyleSheet("QLabel { background-color : white; color : blue; }");
        self.c = None
        self.conn = None
        self.image = None
        
        self.initUI()
        
    def initUI(self):
        #testing UI code
        self.lbl1 = QtGui.QLabel('Tag this entry:', self)
        self.lbl1.move(15, 10)

        self.combo = QtGui.QComboBox(self)      
        self.combo.move(15, 25)
        
        self.btn1 = QtGui.QPushButton('Tag', self)
        self.btn1.resize(50,25)
        self.btn1.move(100, 23)
         
        self.lbl2 = QtGui.QLabel('Add a new tag:', self)
        self.lbl2.move(15, 45)     

        self.tf1 = QtGui.QLineEdit(self)
        self.tf1.move(15,60)   

        self.btn2 = QtGui.QPushButton('Add', self)
        self.btn2.resize(50,25)
        self.btn2.move(160, 60)
        
        self.lbl3 = QtGui.QLabel('', self)
        self.lbl3.move(15, 90)   

        self.lbl4 = QtGui.QLabel( "" , self)
        self.lbl4.move(15, 120)    
        
        #self.ta1 = QtGui.QTextEdit(self)
        #self.ta1.move(15, 120)  

        self.btn2.clicked.connect(self.onBtn2Click)
        self.btn1.clicked.connect(self.onBtn1Click)                
        
    def onBtn1Click(self): 
    
        # do we know about this image? If not, add it to images
        t = ( str(self.image), )
        self.c.execute("SELECT * FROM images where images.location =?", t)
        this_img = self.c.fetchone()
        if this_img is None:
            print "setting image"
            im = (str(self.image),)
            self.c.execute("INSERT INTO images VALUES (?)", im )
            self.conn.commit()
            
        #get the rowids    
        self.c.execute("SELECT rowid FROM images where images.location =?", t)
        img_row = self.c.fetchone()
        t= (str(self.combo.currentText()),) #will want security later
        self.c.execute("SELECT rowid FROM tags where tags.tag =?", t)
        tag_row = self.c.fetchone()
        
        #tag the image
        print "Attempting to tag"
        v = (str(img_row[0]), str(tag_row[0]),)
        print v
        self.c.execute("INSERT INTO my_tags VALUES (?,?)", v )
        self.conn.commit()
        self.displayTags()
    
    def onBtn2Click(self):
        self.combo.addItem(self.tf1.text())
        self.combo.adjustSize()
        self.lbl3.setText("Tag '" + self.tf1.text() + "' created.")
        self.lbl3.adjustSize()
        v = (str(self.tf1.text()),)
        self.c.execute("INSERT INTO tags VALUES (?)", v )
        self.conn.commit()
        
    def setCurrentImage(self,image): 
        self.image = image
        self.displayTags()
        
    def displayTags(self):
        self.lbl4.setText("The image " + str(self.image) + " has the following tags:")
     
        print "tags on this image"
        t = ( str(self.image), )
        self.c.execute("SELECT tags.tag FROM my_tags, images, tags where my_tags.img = images.rowid and my_tags.tag = tags.rowid and images.location =?", t)
        #self.c.execute("SELECT * FROM  my_tags, images WHERE my_tags.img = images.rowid and images.location =?", t)
        tags_to_list = self.c.fetchone()
        while tags_to_list is not None:
            print tags_to_list
            self.lbl4.setText( "" + str(self.lbl4.text()) + '\n' + str(tags_to_list[0]) )
            tags_to_list = self.c.fetchone()
        self.lbl4.adjustSize()
            
            
    def setConnections(self, c, conn):
        self.c = c
        self.conn = conn
                    
        print "Tags that exist"
        self.c.execute("SELECT * from tags")
        tags_to_list = c.fetchone()
        while tags_to_list is not None:
            print tags_to_list
            self.combo.addItem(tags_to_list[0])
            tags_to_list = c.fetchone()
            
        print "Images that exist"
        self.c.execute("SELECT * from images")
        tags_to_list = c.fetchone()
        while tags_to_list is not None:
            print tags_to_list
            tags_to_list = c.fetchone()
            
        print "My_tags that exist"
        self.c.execute("SELECT * from my_tags")
        tags_to_list = c.fetchone()
        while tags_to_list is not None:
            print tags_to_list
            tags_to_list = c.fetchone()


class Window(QtGui.QLabel):
    current_image = None
    image_list = None
    zoom = 0
    conn = None
    c = None
    tag_creator_popup = None;

    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)

        self.image_list = ImageList()
        self.image_list.load_dir()
        self.image_list.loop = True
        self.zoom = 0
        
        #print len(sys.argv)
        #print sys.argv[1]
        if len(sys.argv) > 1: #open the image given as a parameter, othewise open the first image in the directory
             self.image_list.startAt(sys.argv[1])

        #basic look of the window     
        self.setGeometry(300, 300, 1000, 700)
        self.setWindowTitle('Window')
        self.setAlignment(Qt.AlignCenter) 
        self.setStyleSheet("QLabel { background-color : white; color : blue; }");

        #display the image
        self.load_image(self.image_list.current())
        self.setWindowTitle(self.image_list.current())
        
        #load the tag database, create it if it is not there
        if os.path.exists("image_tags.db"):
            self.conn = sqlite3.connect('image_tags.db')
            self.c =  self.conn.cursor()
            print "found"
        else:
            self.conn = sqlite3.connect('image_tags.db')
            self.c =  self.conn.cursor()
            
            # Create table
            self.c.execute('''CREATE TABLE images
            (location)''')
            self.c.execute('''CREATE TABLE tags
            (tag)''')
            self.c.execute('''CREATE TABLE my_tags
            (img, tag)''')

            # Save (commit) the changes
            self.conn.commit()
            print "created"


    def load_image(self, filename):
        # is it a gif or other image?
        if os.path.splitext(filename)[1] == ".gif":
            # print "This is a gif!"
            movie = QtGui.QMovie(filename)
            self.setMovie(movie)
            movie.start()
            return

        if not self.current_image:
            self.current_image = QtGui.QImage()
        self.current_image.load(filename)
        if self.current_image.width() > self.width():
            self.current_image = self.current_image.scaledToWidth(self.width(),1)
        if self.current_image.height() > self.height():
            self.current_image = self.current_image.scaledToHeight(self.height(),1)
        self.setPixmap(QtGui.QPixmap.fromImage(self.current_image))

    def keyPressEvent(self, event):
        # print "key pressed!"
        # print event.key()

        if event.key() == Qt.Key_Q:
            self.close() #needs to also close popup

        if event.key() == Qt.Key_Right:
            self.zoom = 0
            if not self.image_list.at_end():
                self.load_image(self.image_list.next())
            self.setWindowTitle(self.image_list.current())
            
            # self.setGeometry(
            #     300,
            #     300,
            #     self.current_image.width(),
            #     self.current_image.height()
            # )

        if event.key() == Qt.Key_Left:
            self.zoom = 0
            if not self.image_list.at_beginning():
                self.load_image(self.image_list.previous())
            self.setWindowTitle(self.image_list.current())
            

        #fullscreen
        if event.key() == Qt.Key_F:
            self.showFullScreen()

        #turn off fullscreen
        if event.key() == Qt.Key_G:
            self.showNormal()
        
        #set zoom back to 0
        if event.key() == Qt.Key_0:
            #
            self.zoom = 0
            self.load_image(self.image_list.current())
        
        #open the tagging interface
        if event.key() == Qt.Key_A:
            self.tag_creator_popup = Tag_Creation_Popup()
            self.tag_creator_popup.setConnections(self.c,  self.conn)
            self.tag_creator_popup.setCurrentImage(self.image_list.current());
            self.tag_creator_popup.show()
        
    def wheelEvent(self, event):
        # can currently only zoom into the center
        # smooth or fast scale should eventually be a setting option
        # can be slow

        if self.movie() is not None: #prevents scrolling on animated gif
            return
        if (((self.width() + (self.zoom + event.delta())) > 0) and ((self.height() + (self.zoom + event.delta())) > 0) and (self.zoom + event.delta() < 10000)): #keeps the image from getting to small or too big
            self.zoom += event.delta()
            self.load_image(self.image_list.current())
            self.current_image = self.current_image.scaledToHeight(self.height() + self.zoom,1)
            self.current_image = self.current_image.scaledToWidth(self.width() + self.zoom,1)
            self.setPixmap(QtGui.QPixmap.fromImage(self.current_image))
            
    def resizeEvent(self, event):
        self.zoom = 0
        self.load_image(self.image_list.current())
        
  

app = QtGui.QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
