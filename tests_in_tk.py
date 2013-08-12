
import os
import Tkinter as tk
from PIL import Image, ImageTk

# options.. sort of
#resize_method = Image.ANTIALIAS
resize_method = Image.NEAREST

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
    ]
    pos = 0 
    imglist = None

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
            return self.imglist[self.pos]
        else:
            raise IOError("No more images in the list!")

    def previous(self):
        if self.pos > 0:
            self.pos -= 1
            return self.imglist[self.pos]
        else:
            raise IOError("No fewer images in the list!")

    def at_end(self):
        return self.pos >= (len(self.imglist) - 1)

    def at_beginning(self):
        return self.pos == 0


class ImageViewer(object):
    root = None
    imglist = ImageList()
    panel = None
    fullscreen = False

    def __init__(self):
        self.imglist.load_dir()

        self.root = tk.Tk()
        self.root.title('ImageViewer')
        self.root.configure(background='black')
        #root.overrideredirect(True) # borderless root window?
        #root.attributes('-toolwindow', True)

        self.root.bind("<Key>", self.on_keypress)

        self.load_image(self.imglist.current())


        # start the event loop
        self.root.mainloop()

    def on_keypress(self, event):
        """dispatch keys"""
        global fullscreen


        if event.char == 'q':
            self.root.quit()
            return


        if event.char == 'f':
            self.fullscreen = not self.fullscreen
            self.root.attributes('-fullscreen', self.fullscreen)
            self.load_image(self.imglist.current())
            return

        if event.keysym == 'Right':
            # move to the next picture
            try:
                self.load_image(self.imglist.next())
            except IOError:
                pass
            return

        if event.keysym == 'Left':
            # move to the prev picture
            try:
                self.load_image(self.imglist.previous())
            except IOError:
                pass
            return
        
        if event.char == '0':
            self.imglist.pos = 0
            self.load_image(self.imglist.current())
            return

        # print "pressed", repr(event.char), event.keysym, type(event.keysym)


    def load_image(self, filename):

        # if there is an existing image, destroy it
        if self.panel is not None:
            self.panel.destroy()


        pil_image = Image.open(filename)

        if self.panel is not None:
            newsize = self.root.winfo_width(), self.root.winfo_height()
            if newsize[0] < pil_image.size[0] or newsize[1] < pil_image.size[1]:
                pil_image.thumbnail(newsize, resize_method)
        #pil_image = pil_image.resize([int(0.5 * s) for s in pil_image.size])
        #pil_image = pil_image.resize([int(ratio * s) for s in pil_image.size])

        image1 = ImageTk.PhotoImage(pil_image)

        # get the image size
        w = image1.width()
        h = image1.height()

        # position coordinates of root 'upper left corner'
        x = 0
        y = 0

        if self.panel is None:
            print "This is the first image, so resizing the window to fit it."
            # resize only if this is the first image opened
            # make the root window the size of the image
            self.root.geometry("%dx%d+%d+%d" % (w, h, x, y))

        # root has no image argument, so use a label as a panel
        self.panel = tk.Label(self.root, image=image1)
        self.panel.configure(background='black')
        self.panel.pack(side='top', fill='both', expand='yes')

        # put a button on the image panel to test it
        #button2 = tk.Button(panel1, text='button2')
        #button2.pack(side='top')

        # save the panel's image from 'garbage collection'
        self.panel.image = image1

        return

if __name__ == "__main__":
    ImageViewer()

