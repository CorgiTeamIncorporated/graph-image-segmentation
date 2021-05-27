import tkinter as tk
from tkinter import Frame, Label, ttk
from tkinter import filedialog as fd
from tkinter.constants import *
from PIL import Image, ImageTk
import math


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        #self.is_first_click = True
        self.count_click = 0
        self.pack()
        self.create_top_panel()

    def create_top_panel(self):
        self.master.update()
        self.f_top = Frame(self.master, height = 50, width=self.master.winfo_width())
        open_button = ttk.Button(self.f_top, text = 'Open a File',command = self.select_file)
        self.text_label = Label(text = 'Click on the object')
        self.text_label.place(x = 100, y = 6)
        #self.text_label
        self.f_top.place(x = 5, y = 5)
        open_button.pack(expand = True)

    ''' def say_hi(self, event):
        print("hi there, everyone!", event.x, event.y)'''
    
    def select_file(self):
        filetypes = (
            ('Images', '*.png *.jpg *.jpeg *.bmp'),
            ('PNG', '*.png'),
            ('JPG', '*.jpg'),
            ('JPEG', '*.jpeg'),
            ('BMP', '*.bmp')
        )

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir = '/',
            filetypes = filetypes)

        print(filename)

        if hasattr(self, 'photo_label'):
            self.photo_label.destroy()
        self.place_image(filename)
    
    
    def place_image(self, filename):
        image = Image.open (filename) 
        self.photo = ImageTk.PhotoImage (image) 

        self.photo_label = tk.Label (image = self.photo, height = self.photo.height(), width = self.photo.width()) 
        self.photo_label.image = self.photo    
        self.photo_label.place (x = 10 , y = 50)
        self.photo_label.bind('<ButtonRelease>', self.click_image)

        self.place_mask(image)

    def place_mask(self, image = None):
        print('place_mask')
        self.mask = ImageTk.PhotoImage (image) 

        self.mask_label = tk.Label (image = self.mask, height = self.mask.height(), width = self.mask.width()) 
        self.mask_label.image = self.mask    
        self.mask_label.place (x = 800 , y = 50)

    def click_image(self, event):
        self.count_click += 1
        if self.count_click == 1:
            print("tik1 ", event.x, ' ', event.y)
            self.text_label.text = 'Click on the background'
        if self.count_click == 2:
            print("tik2 ", event.x, ' ', event.y)
            self.text_label.destroy()
            #вызвать создание радиобаттон
            #отправить в сегментацию
        if self.count_click > 2:
            print("tik3 ", event.x, ' ', event.y)

        
        
        '''if self.is_first_click:
            #self.text_label = Label(self.f_top, text = 'Click on the object')
            #self.text_label.place(x = 100, y = 6)
            print("tik ", event.x, ' ', event.y)
            self.text_label.text = 'Click on the background'
            print("tik ", event.x, ' ', event.y)'''




root = tk.Tk()
root.title('Tkinter Open File Dialog')
root.resizable(False, False)
root.geometry('1500x750')

app = Application(master=root)
app.mainloop()


def create_label():
    label1 = tk.Label (height = 700, width = 700) 
    label1.place (x = 0 , y = 50)
    label1.config(background='red')

    label2 = tk.Label (height = 700, width = 700)
    label2.place (x = 700 , y = 50)
    label2.config(background='green')



    ''' root.update()
    
    factor = min(label1.winfo_width()/photo.width(), label1.winfo_height()/photo.height())
    print(factor)

    image = image1.resize ((math.ceil(factor*photo.width()), math.ceil(factor*photo.height())))
    photo = ImageTk.PhotoImage (image)  
    label1 = tk.Label (image = photo, height = 500, width = 1000) 
    label1.image = photo
    label1.place (x = 0 , y = 0)'''




#root.update()
#f_top = Frame(root, height = 50, width=root.winfo_width())
#f_top.config(background='red')
#open_button = ttk.Button( f_top, text = 'Open a File',command = select_file)

#f_top.place(x = 5, y = 5)
#open_button.pack(expand = True)

#create_label()



#root.mainloop()
