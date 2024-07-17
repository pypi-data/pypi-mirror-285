import re, httpx, io, os, bs4
from PIL import ImageTk, Image
from bs4 import BeautifulSoup
from .custom_widgets import Textarea
from tkinter import (
    Tk,
    ttk,
    Entry,
    Label,
    Button,
    Checkbutton,
    filedialog,
    Radiobutton,
    font,
    OptionMenu,
    StringVar,
)

class RenderKit(Tk):
    def __init__(self,
                html: str,
                width: int = 500,
                height: int = 500,
                background = None
            ) -> None:
        super().__init__()
        self._widgets: dict = {}

        self.display(html)

        if background:
            background(self)

        self.geometry(f"{width}x{height}")
        self.mainloop()

    def get(self, widget_id: str):
        return self._widgets.get(widget_id, None)

    def display(self, html: str) -> None:
        parser = BeautifulSoup(html, "html.parser")

        for tag in parser.find_all(True):

            id: str = tag.get("id") if tag.get("id") else ""

            alignments: dict = {"left": "w", "right": "e", "top": "n", "bottom": "s"}
            alignment: str = tag.get("align")

            if alignment and "center" not in alignment:
                alignment = "".join([alignments.get(i, "") for i in alignment.split(" ")])
            elif alignment and alignment == "center":
                pass
            else:
                alignment = "nw"

            if tag.name == "title":
                self.title(tag.text)

            elif tag.name.startswith("h") and len(tag.name) == 2:
                font_sizes: dict = {"h1": 32, "h2": 26, "h3": 24, "h4": 20, "h5" : 18}
                font_size = font.Font(size=font_sizes.get(tag.name, 14))

                heading = Label(self, text=tag.text, font=font_size)
                heading.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = heading

            elif tag.name == "p":
                paragraph = Label(self, text=tag.text)
                paragraph.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = paragraph

            elif tag.name == "input" and tag.get("type") == "text":
                text_input = Entry(self)
                text_input.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = text_input

            elif tag.name == "input" and tag.get("type") == "password":
                passwd_input = Entry(self, show="*")
                passwd_input.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = passwd_input

            elif tag.name == "input" and tag.get("type") == "checkbox":
                checkbox = Checkbutton(self)
                checkbox.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = checkbox

            elif tag.name == "input" and tag.get("type") == "radio":
                radio = Radiobutton(self)
                radio.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = radio

            elif tag.name == "input" and tag.get("type") == "file":
                file_upload = Button(self, text="Select File")
                file_upload.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = file_upload

            elif tag.name == "textarea":
                textarea = Textarea(self)
                textarea.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = textarea

            elif tag.name == "button":
                button = Button(self, text=tag.text)
                button.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = button

            elif tag.name == "select":
                options: list = [option.text for option in tag.find_all("option")]

                inital_value = StringVar(self)
                inital_value.set(options[0])

                select_menu = OptionMenu(self, inital_value, *options)
                select_menu.pack(padx=2, pady=2, anchor=alignment)

                if id:
                    self._widgets[id] = select_menu

            elif tag.name == "img":
                image_src = tag.get("src", "")
                image_height = tag.get("height", "")
                image_width = tag.get("width", "")
                image_content = None

                if re.match(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', image_src):
                    image_content = httpx.get(image_src).content
                    image_content = Image.open(io.BytesIO(image_content))
                elif os.path.exists(image_src):
                    image_content = Image.open(image_src)
                else:
                    continue

                if image_content:
                    if image_width and image_height:
                        image_content = image_content.resize((int(image_width), int(image_height)))
                    image = ImageTk.PhotoImage(image_content)
                    image_label = Label(self, image=image)
                    image_label.image = image
                    image_label.pack(padx=2, pady=2, anchor=alignment)

                    if id:
                        self._widgets[id] = image_label

    def addEventListener(self, widget, name, handler) -> None:
        events = {
            "click": "<Button-1>",
            "double_click": "<Double-Button-1>",
            "triple_click": "<Triple-Button-1>",
            "middle_click": "<Button-2>",
            "right_click": "<Button-3>",
            "scroll_up": "<Button-4>",
            "scroll_down": "<Button-5>",
            "button_release": "<ButtonRelease-1>",
            "return_press": "<Return>",
            "enter": "<Enter>",
            "leave": "<Leave>",
            "motion": "<Motion>",
            "key_press": "<KeyPress>",
            "key_release": "<KeyRelease>",
            "focus_in": "<FocusIn>",
            "focus_out": "<FocusOut>",
            "destroy": "<Destroy>",
            "visibility": "<Visibility>",
            "mouse_wheel": "<MouseWheel>",
            "file": None
        }

        if name in events:
            if name == "file":
                widget.bind(events["click"], lambda e: handler(name, e, filedialog.askopenfilename()))
                return None

            widget.bind(events[name], lambda e: handler(name, e))
