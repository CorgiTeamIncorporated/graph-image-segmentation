import tkinter as tk
from tkinter import StringVar

from PIL import Image, ImageDraw, ImageTk


def get_circle_bounding_box(center_x, center_y, radius):
    return (center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius)


class SegmentatorGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.pack(fill=tk.BOTH, expand=1)

        # TODO: implement radius changing with slider
        # Radius of brush
        self.radius = 5

        # Defines canvas border
        self.offset_x = 0
        self.offset_y = 0

        # Defines which brush is currently selected
        self._point_type = StringVar()
        self._point_type.set('object')

        # Initial phase is phase when both
        # background and object are needed to be marked
        # Main phase follows initial step
        self._phase = 'initial'

        # Only needed during initial phase
        self._is_object_selected = False
        self._is_background_selected = False

        # Colors of brushes
        self._colors = {
            'object': (255, 0, 0, 100),
            'background': (0, 0, 255, 100)
        }

        # Colors of mask
        self._mask_colors = {
            'object': 1,
            'background': 2
        }

        # Mask of background and object points
        # Selected during one iteration
        # This is not presented to user

        # TODO: Load image interactively
        filename = './static/banana1-gr-320.jpg'
        self.orig_image = Image.open(filename).convert('RGBA')
        self.mask_image = Image.new('RGBA', self.orig_image.size)

        self._init_ui()
        self._update_displayed_image()
        self._init_binds()

        self._mask = Image.new('L', self.orig_image.size, 0)

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
            padx=10,
            pady=10
        )
        self._canvas_frame.grid(row=1, column=2, sticky=tk.NS)

        self.canvas = tk.Canvas(self._canvas_frame,
                                width=self.orig_image.size[0],
                                height=self.orig_image.size[1])
        self.canvas.grid(row=1, column=2)

    def _init_ui(self):
        self.pack(padx=20, pady=20)

        self._init_toolbox()
        self._init_canvas()

    def _init_binds(self):
        self.canvas.bind('<Motion>', self.cursor_motion_handler)
        self.canvas.bind('<B1-Motion>', self.pressed_cursor_motion_handler)
        self.canvas.bind('<ButtonRelease-1>', self.cursor_release_handler)

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
        # Clear cursor before drawing
        self.pointer_image = Image.new('RGBA', self.orig_image.size)

        box = get_circle_bounding_box(event.x - self.offset_x,
                                      event.y - self.offset_y,
                                      self.radius)

        ImageDraw.Draw(self._mask).ellipse(
            box, fill=self._mask_colors[self._point_type.get()]
        )
        ImageDraw.Draw(self.mask_image).ellipse(
            box, fill=self._colors[self._point_type.get()]
        )

        self._update_displayed_image()

    def cursor_release_handler(self, _):
        if self._phase == 'initial':
            point_type_str = self._point_type.get()
            self._is_object_selected |= (point_type_str == 'object')
            self._is_background_selected |= (point_type_str == 'background')

            if self._is_object_selected and self._is_background_selected:
                # Send mask to segmentator
                self._phase = 'main'
                pass
        else:
            # Send mask to segmentator
            self._mask = Image.new('L', self.orig_image.size, 0)
            pass


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Graph Image Segmentation')
    root.resizable(False, False)
    root.geometry('800x600')

    app = SegmentatorGui(master=root)
    app.mainloop()
