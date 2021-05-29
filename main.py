import numpy as np
import tkinter as tk
from itertools import product
from tkinter import IntVar, StringVar
from tkinter import filedialog as fd
from tkinter import ttk

from PIL import Image, ImageDraw, ImageTk

from algo.image_segmentation import Segmentator
from algo.utils import correctness_ratio, generate_mask, jaccard_score


def get_circle_bounding_box(center_x, center_y, radius):
    return (center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius)


class SegmentatorGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.pack(fill=tk.BOTH, expand=1)

        # Radius of brush
        self.radius = IntVar()
        self.radius.set(5)

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

        # Only needed before picture opening
        self._is_picture_opened = False

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

        # Empty picture on first start
        self.orig_image = Image.new('RGBA', (300, 300))

        self._init_ui()
        self._init_binds()

    def _ask_filename(self):
        filetypes = (
            ('Images', '*.png *.jpg *.jpeg *.bmp'),
            ('PNG', '*.png'),
            ('JPG', '*.jpg'),
            ('JPEG', '*.jpeg'),
            ('BMP', '*.bmp')
        )

        filename = fd.askopenfilename(
            title='Open a picture',
            initialdir='./',
            filetypes=filetypes
        )

        self.orig_image = Image.open(filename).convert('RGBA')
        self.mask_image = Image.new('RGBA', self.orig_image.size)

        self.segmentator = Segmentator(self.orig_image.convert('L'),
                                       neighbors=8)
        self._phase = 'initial'

        # Mask of background and object points
        # Selected during one iteration
        # This is not presented to user
        self._mask = Image.new('L', self.orig_image.size, 0)

        self._update_displayed_image()
        self._is_picture_opened = True

    def _ask_thuth_mask_file(self):
        filetypes = (
            ('Images', '*.png *.jpg *.jpeg *.bmp'),
            ('PNG', '*.png'),
            ('JPG', '*.jpg'),
            ('JPEG', '*.jpeg'),
            ('BMP', '*.bmp')
        )

        filename = fd.askopenfilename(
            title='Open a mask',
            initialdir='./',
            filetypes=filetypes
        )

        self.ground_truth_mask_image = Image.open(filename).convert('L')

        self.truth_tk_image = ImageTk.PhotoImage(self.ground_truth_mask_image)
        self.displayed_ground_truth = self.ground_truth.create_image(
            self.offset_x,
            self.offset_y,
            image=self.truth_tk_image,
            anchor=tk.NW
        )

    def _init_toolbox(self):
        self._toolbox_frame = tk.LabelFrame(
            self,
            text='Toolbox',
            relief=tk.RIDGE,
            padx=10
        )
        self._toolbox_frame.grid(row=1, column=1, sticky=tk.NS)

        self._open_button = ttk.Button(self._toolbox_frame,
                                       text='Open a picture',
                                       command=self._ask_filename)
        self._open_button.grid(row=1, column=1)

        self._mark_as_frame = tk.LabelFrame(
            self._toolbox_frame,
            text="Mark as",
            relief=tk.RIDGE
        )
        self._mark_as_frame.grid(row=2, column=1, pady=10)

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

        self._slider = tk.Scale(self._toolbox_frame,
                                from_=1,
                                to=40,
                                variable=self.radius,
                                orient=tk.HORIZONTAL,
                                relief=tk.RIDGE,
                                label='Pointer Radius')
        self._slider.grid(row=3, column=1)

        self._open_gt_button = ttk.Button(self._toolbox_frame,
                                          text='Open a ground truth mask',
                                          command=self._ask_thuth_mask_file)
        self._open_gt_button.grid(row=4, column=1, pady=10)

    def _init_metrics(self):
        self._metrics_frame = tk.LabelFrame(
            self,
            text='Metrics',
            relief=tk.RIDGE,
            padx=10
        )
        self._metrics_frame.grid(row=2, column=1, sticky=tk.NS)

        self._jaccard_metric = ttk.Label(self._metrics_frame,
                                         text='Jaccard: -')
        self._jaccard_metric.grid(row=1, column=1)

        self._correctness_metric = ttk.Label(self._metrics_frame,
                                             text='Correctness ratio: -')
        self._correctness_metric.grid(row=2, column=1)

    # GUI initialization functions
    def _init_canvas(self):
        self._canvas_frame = tk.LabelFrame(
            self,
            text='Canvas',
            relief=tk.RIDGE,
            padx=10,
            pady=10
        )
        self._canvas_frame.grid(row=1, column=2, sticky=tk.NS+tk.E)

        self.canvas = tk.Canvas(self._canvas_frame,
                                width=self.orig_image.width,
                                height=self.orig_image.height)
        self.canvas.grid(row=1, column=2)

    def _init_ground_truth_mask(self):
        self._ground_truth_frame = tk.LabelFrame(
            self,
            text='Ground truth mask',
            relief=tk.RIDGE,
            padx=10,
            pady=10
        )
        self._ground_truth_frame.grid(row=1, column=3, sticky=tk.NS+tk.E)

        self.ground_truth = tk.Canvas(self._ground_truth_frame,
                                      width=self.orig_image.width,
                                      height=self.orig_image.height)
        self.ground_truth.grid(row=1, column=3)

    def _init_ui(self):
        self.pack(padx=20, pady=20)

        self._init_toolbox()
        self._init_metrics()
        self._init_canvas()
        self._init_ground_truth_mask()

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

        self.canvas.configure(width=self.orig_image.width,
                              height=self.orig_image.height)

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

    def _update_metrics(self, s, t):
        if hasattr(self, 'ground_truth_mask_image'):
            mask_true = np.array(self.ground_truth_mask_image)
            mask_ours = generate_mask(s, t, mask_true.shape)
            jm = jaccard_score(mask_true, mask_ours)
            self._jaccard_metric.config(text='Jaccard: ' + str(jm))
            cm = correctness_ratio(mask_true, mask_ours)
            self._correctness_metric.config(text='Correctness ratio: ' + str(cm))

    # Event handlers
    def cursor_motion_handler(self, event):
        self.pointer_image = Image.new('RGBA', self.orig_image.size)
        ImageDraw.Draw(self.pointer_image).ellipse(
            get_circle_bounding_box(event.x - self.offset_x,
                                    event.y - self.offset_y,
                                    self.radius.get()),
            fill=self._colors[self._point_type.get()]
        )
        self._update_displayed_image()

    def pressed_cursor_motion_handler(self, event):
        if self._is_picture_opened:
            # Clear cursor before drawing
            self.pointer_image = Image.new('RGBA', self.orig_image.size)

            box = get_circle_bounding_box(event.x - self.offset_x,
                                          event.y - self.offset_y,
                                          self.radius.get())

            ImageDraw.Draw(self._mask).ellipse(
                box, fill=self._mask_colors[self._point_type.get()]
            )
            ImageDraw.Draw(self.mask_image).ellipse(
                box, fill=self._colors[self._point_type.get()]
            )

            self._update_displayed_image()

    def cursor_release_handler(self, _):
        def extract_marked_pixels(image: Image.Image):
            object_pixels = set()
            background_pixels = set()

            for pixel in product(range(image.width), range(image.height)):
                if image.getpixel(pixel) == self._mask_colors['object']:
                    object_pixels.add(pixel)

                if image.getpixel(pixel) == self._mask_colors['background']:
                    background_pixels.add(pixel)

            return object_pixels, background_pixels

        def start_segmentation():
            print('segmentation started')

            object_pixels, background_pixels = extract_marked_pixels(
                self._mask
            )
            s, t = self.segmentator.mark(
                object_pixels=object_pixels,
                background_pixels=background_pixels
            )

            print('segmentation completed')

            for pixel in s:
                if pixel != 's':
                    self.mask_image.putpixel(pixel,
                                             self._colors['object'])
            for pixel in t:
                if pixel != 't':
                    self.mask_image.putpixel(pixel,
                                             self._colors['background'])

            # Clear temp mask
            self._mask = Image.new('L', self.orig_image.size, 0)
            self._update_displayed_image()
            self._update_metrics(s, t)

        if self._phase == 'initial':
            point_type_str = self._point_type.get()
            self._is_object_selected |= (point_type_str == 'object')
            self._is_background_selected |= (point_type_str == 'background')

            if self._is_object_selected and self._is_background_selected:
                start_segmentation()
                self._phase = 'main'
        else:
            start_segmentation()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Graph Image Segmentation')
    root.resizable(False, False)
    root.geometry('1200x800')

    app = SegmentatorGui(master=root)
    app.mainloop()
