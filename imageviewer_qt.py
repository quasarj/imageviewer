#!/usr/bin/env python

import sys
import os
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
            
        
         


class Window(QtGui.QLabel):
    current_image = None
    image_list = None
    zoom = 0

    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)

        self.image_list = ImageList()
        self.image_list.load_dir()
        self.image_list.loop = True
        self.zoom = 0
        
        #print len(sys.argv)
        #print sys.argv[1]
        if len(sys.argv) > 1:
             self.image_list.startAt(sys.argv[1])

        self.setGeometry(300, 300, 1000, 700)
        self.setWindowTitle('Window')
        self.setAlignment(Qt.AlignCenter) 
        self.setStyleSheet("QLabel { background-color : white; color : blue; }");

        self.load_image(self.image_list.current())
        self.setWindowTitle(self.image_list.current())

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
        #print self.current_image.width()
        if self.current_image.width() > self.width():
            self.current_image = self.current_image.scaledToWidth(self.width(),1)
        if self.current_image.width() > self.height():
            self.current_image = self.current_image.scaledToHeight(self.height(),1)
        self.setPixmap(QtGui.QPixmap.fromImage(self.current_image))

    def keyPressEvent(self, event):
        # print "key pressed!"
        # print event.key()

        if event.key() == Qt.Key_Q:
            self.close()

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
            


        ## disabled for now, need to figure out how to return
        ## from fullscreen mode

        if event.key() == Qt.Key_F:
            self.showFullScreen()


        # if event.key() == Qt.Key_G:
        #     print "switching back to normal?"
        #     self.hide()
        #     self.showNormal()
        
        if event.key() == Qt.Key_0:
            self.zoom = 0
            self.load_image(self.image_list.current())
        
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
        

app = QtGui.QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
