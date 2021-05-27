import tkinter as tk
from tkinter import Frame, Label, Radiobutton, StringVar, ttk, messagebox
from tkinter import filedialog as fd
from tkinter.constants import *
from PIL import Image, ImageTk
import math


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.count_click = 0
        self.pack()
        self.create_top_panel()

    def create_top_panel(self):
        self.master.update()
        self.f_top = Frame(self.master, height = 50, width=self.master.winfo_width())
        open_button = ttk.Button(self.f_top, text = 'Open a File',command = self.select_file)
        self.text_label = Label(text = 'Click on the object')
        self.text_label.place(x = 100, y = 6)
        self.f_top.place(x = 5, y = 5)
        open_button.pack(expand = True)

    
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

    def place_mask(self, image = None):
        self.mask = ImageTk.PhotoImage (image) 

        self.mask_label = tk.Label (image = self.mask, height = self.mask.height(), width = self.mask.width()) 
        self.mask_label.image = self.mask    
        self.mask_label.place (x = 800 , y = 50)

    def click_image(self, event):
        self.count_click += 1

        if self.count_click == 1:
            self.first_coord_obj = self.choice_pixels(event.x, event.y, 10)
            self.text_label.destroy()
            self.text_label = Label(text = 'Click on the background')
            self.text_label.place(x = 100, y = 6)

        if self.count_click == 2:
            self.first_coord_bg = self.choice_pixels(event.x, event.y, 10)
            self.text_label.destroy()
            self.create_radiobutton()
            #отправить в сегментацию
            #mask_image = 'функция сигментации'(self.photo, self.first_coord_obj, self.first_coord_bg)            
            #self.mask_label.destroy()
            #self.place_mask(mask_image)

        if self.count_click > 2:
            coord = self.choice_pixels(event.x, event.y, 1)

            if self.point_type.get() != 'Object' and self.point_type.get() != 'Background':
                messagebox.showinfo("Attention", "Select Object or Background")
            else:
                print("")
                #отправить в сегментацию
                #mask_image = 'функция сигментации'(self.photo, coord, self.point_type.get())            
                #self.mask_label.destroy()
                #self.place_mask(mask_image)

    def create_radiobutton(self):
        self.point_type = StringVar()
        r1 = Radiobutton(text = 'Object', variable = self.point_type, value = 'Object')
        r2 = Radiobutton(text = 'Background',variable = self.point_type, value = 'Background')
        r1.place(x = 100, y = 6)
        r2.place(x = 100, y = 25)

    def choice_pixels(self, place_x, place_y, radius):
        result = set()
        for x in range(place_x - radius, place_x + radius + 1):
            for y in range(place_y - radius, place_y + radius + 1):
                result.add((x,y))
        return(result)


root = tk.Tk()
root.title('Tkinter Open File Dialog')
root.resizable(False, False)
root.geometry('1500x750')

app = Application(master=root)
app.mainloop()