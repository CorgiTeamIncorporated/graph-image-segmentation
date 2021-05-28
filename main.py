import tkinter as tk
# from tkinter import Frame, Label, Radiobutton, StringVar, ttk, messagebox
# from tkinter import filedialog as fd
# from tkinter.constants import *
from PIL import Image, ImageTk, ImageDraw
from tkinter import StringVar
# import math


def get_circle_bounding_box(center_x, center_y, radius):
    return (center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius)


class SegmentatorGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.pack(fill=tk.BOTH, expand=1)

        self.radius = 5

        self.offset_x = 10
        self.offset_y = 10

        self._point_type = StringVar()
        self._point_type.set('object')

        self._colors = {
            'object': (255, 0, 0, 100),
            'background': (0, 0, 255, 100)
        }

        # TODO: Load image interactively
        filename = './static/banana1-gr-320.jpg'
        self.orig_image = Image.open(filename).convert('RGBA')
        self.mask_image = Image.new('RGBA', self.orig_image.size)

        self._init_ui()
        self._update_displayed_image()
        self._init_binds()

    def _init_toolbox(self):
        self._toolbox_frame = tk.LabelFrame(
            self,
            text='Toolbox',
            relief=tk.RIDGE,
            padx=10
        )
        self._toolbox_frame.grid(row=1, column=1, sticky=tk.NS)

        self._mark_as_frame = tk.LabelFrame(
            self._toolbox_frame,
            text="Mark as",
            relief=tk.RIDGE
        )

        self._object_radio = tk.Radiobutton(
            self._mark_as_frame,
            text='Object',
            variable=self._point_type,
            value='object'
        )
        self._object_radio.grid(row=1, column=1)

        self._background_radio = tk.Radiobutton(
            self._mark_as_frame,
            text='Background',
            variable=self._point_type,
            value='background'
        )
        self._background_radio.grid(row=2, column=1)

        self._mark_as_frame.grid(row=1, column=1)

    # GUI initialization functions
    def _init_canvas(self):
        self._canvas_frame = tk.LabelFrame(
            self,
            text='Canvas',
            relief=tk.RIDGE,
            padx=10
        )
        self._canvas_frame.grid(row=1, column=2, sticky=tk.NS)

        self.canvas = tk.Canvas(self._canvas_frame, width=500, height=500)
        self.canvas.grid(row=1, column=2)

    def _init_ui(self):
        self.pack(padx=20, pady=20)

        self._init_toolbox()
        self._init_canvas()

    def _init_binds(self):
        self.canvas.bind('<Motion>', self.cursor_motion_handler)
        self.canvas.bind('<B1-Motion>', self.pressed_cursor_motion_handler)

    def _update_displayed_image(self):
        self.combined_image = self.orig_image.copy()

        if hasattr(self, 'mask_image'):
            self.combined_image.paste(self.mask_image,
                                      mask=self.mask_image)

        if hasattr(self, 'pointer_image'):
            self.combined_image.paste(self.pointer_image,
                                      mask=self.pointer_image)

        self.combined_tk_image = ImageTk.PhotoImage(self.combined_image)

        if hasattr(self, 'displayed_image'):
            self.canvas.itemconfig(self.displayed_image,
                                   image=self.combined_tk_image)
        else:
            self.displayed_image = self.canvas.create_image(
                self.offset_x,
                self.offset_y,
                image=self.combined_tk_image,
                anchor=tk.NW
            )

    # Event handlers
    def cursor_motion_handler(self, event):
        self.pointer_image = Image.new('RGBA', self.orig_image.size)
        ImageDraw.Draw(self.pointer_image).ellipse(
            get_circle_bounding_box(event.x - self.offset_x,
                                    event.y - self.offset_y,
                                    self.radius),
            fill=self._colors[self._point_type.get()]
        )
        self._update_displayed_image()

    def pressed_cursor_motion_handler(self, event):
        self.pointer_image = Image.new('RGBA', self.orig_image.size)
        ImageDraw.Draw(self.mask_image).ellipse(
            get_circle_bounding_box(event.x - self.offset_x,
                                    event.y - self.offset_y,
                                    self.radius),
            fill=self._colors[self._point_type.get()]
        )
        self._update_displayed_image()


root = tk.Tk()
root.title('Graph Image Segmentation')
root.resizable(False, False)
root.geometry('800x600')

app = SegmentatorGui(master=root)
app.mainloop()
