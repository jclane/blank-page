import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk, messagebox, filedialog, font
from os.path import basename, dirname, realpath, join

from jnlogic import File


class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.menu = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file, state="disabled")
        self.file_menu.add_command(label="Save As...", command=self.saveas_file)
        self.file_menu.add_separator()
        self.file_menu.add_cascade(label="Quit", command=lambda: self.destroy())
        self.menu.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = tk.Menu(self.menu, tearoff=False)
        self.edit_menu.add_command(label="Undo", command=self.undo, state="disabled")
        self.edit_menu.add_command(label="Redo", command=self.redo, state="disabled")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut)
        self.edit_menu.add_command(label="Copy", command=self.copy)
        self.edit_menu.add_command(label="Paste", command=self.paste)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All", command=self.select_all, state="disabled")
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)

        self.format_menu = tk.Menu(self.menu, tearoff=False)
        self.format_menu.add_command(label="Font", command=self.set_font)
        self.menu.add_cascade(label="Format", menu=self.format_menu)

        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(label="Help [coming soon]")
        self.help_menu.add_command(label="About jNotes [coming soon]")
        self.menu.add_cascade(label="?", menu=self.help_menu)
        self.config(menu=self.menu)

        self.text = None
        self.curr_file = None
        self.new_file()

    def setup(self):
        """
        Currently this only sets the title for the window.
        Planned to do more later.
        """
        self.title("jNote - " + self.curr_file.file_name)

    def set_button_state(self, *args):
        """
        Enables/disables the save, undo, redo, and select all menu options
        based on whether or not they can actually be used.
        """
        if self.text.edit_modified() and self.curr_file.saved == False:
            self.file_menu.entryconfig(2, state="normal")
            self.edit_menu.entryconfig(0, state="normal")
        else:
            self.file_menu.entryconfig(2, state="disabled")
            self.edit_menu.entryconfig(0, state="disabled")

        if len(self.text.get("1.0", "end-1c")) > 0:
            self.edit_menu.entryconfig(5, state="normal")
        else:
            self.edit_menu.entryconfig(5, state="disabled")

    def add_scrolledtext(self):
        """
        Adds the scrolledtext box to the container frame.
        """
        if self.text and self.text.winfo_exists():
            self.container.destroy()
        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")
        self.text = tkst.ScrolledText(self.container, undo=True, maxundo=-1)
        self.text.pack(expand=True, fill="both")
        self.text.bind("<Enter>", self.set_button_state)
        self.text.bind("<Leave>", self.set_button_state)
        self.text.bind("<<Modified>>", self.set_button_state)

    def new_file(self):
        """
        Creates a new file object.  Then clears container frame and creates a
        new one by calling 'add_scrolledtext'.
        """
        self.curr_file = File(join(dirname(realpath(__file__)) + "\\New File"))
        self.add_scrolledtext()
        self.setup()

    def open_file(self):
        """
        Destroys container frame and creates a new one by calling
        'add_scrolledtext'.  Inserts the data of that file into
        the newly created scrolledtext box.  Then creates a new File
        object and sets the curr_file to that object.
        """
        file_to_open = filedialog.askopenfilename(defaultextension = "txt",
                                                  initialdir = self.curr_file.file_path,
                                                  filetypes=(("Text files", "*.txt"),
                                                  ("All files", "*.*"))
                                                 )
        if file_to_open:
            with open(file_to_open, "r") as f:
                data = f.read()
            self.curr_file = File(file_to_open)
            self.add_scrolledtext()
            self.text.insert("1.0", data)
            self.text.edit_modified(False)
            self.setup()

    def save_file(self):
        """
        Writes text to file and sets saved flag for curr_file to true.
        """
        with open(self.curr_file.file_path, "w+") as f:
            f.write(self.text.get("1.0", "end-1c"))
        self.curr_file.saved = True
        self.text.edit_modified(False)
        self.setup()

    def saveas_file(self):
        """
        Opens file dialog for user to save new file.
        """
        data = self.text.get("1.0", "end-1c")
        save_location = filedialog.asksaveasfilename(defaultextension = "txt",
                                                     initialdir = self.curr_file.file_path,
                                                     filetypes=(("Text files", "*.txt"),
                                                     ("All files", "*.*"))
                                                    )
        if save_location:
            with open(save_location, "w+") as f:
                f.write(data)
            self.curr_file(save_location)
            self.curr_file.saved = True
            self.text.edit_modified(False)
            self.setup()

    def undo(self):
        self.text.edit_undo()
        self.edit_menu.entryconfig(1, state="normal")

    def redo(self):
        try:
            self.text.edit_redo()
        except tk.TclError:
            self.edit_menu.entryconfig(1, state="disabled")

    def cut(self):
        selection = self.text.selection_get()
        self.text.clipboard_append(selection)
        self.text.selection_clear()

    def copy(self):
        selection = self.text.selection_get()
        self.text.clipboard_append(selection)

    def paste(self):
        cursor_index = self.text.index(tk.INSERT)
        self.text.insert(cursor_index, self.text.clipboard_get())

    def select_all(self):
        self.text.tag_add("sel",'1.0','end')

    def set_font(self):
        """
        Opens a new window which allows the user to change the font
        of the scrolledtext widget.
        """

        def onselect(evt, var):
            """
            When a listbox item is selected by the user var will be
            set to the selected item.  The sample_lbl will also be
            changed to reflect the new selection.

            :params evt: Event that triggered the call
            :params var: The variable to set
            """
            w = evt.widget
            ndex = int(w.curselection()[0])
            name = w.get(ndex)
            var.set(name)
            self.sample_lbl.config(font=(self.font_var.get(), self.size_var.get(), self.style_var.get()))

        def set_font():
            """
            Sets the font, style, and size of the scrolledtext field.
            """
            self.text.config(font=(self.font_var.get(), self.size_var.get(), self.style_var.get()))
            self.font_window.destroy()


        self.font_window = tk.Toplevel(self)
        self.font_window.title("Font")
        self.font_window.resizable(0, 0)

        self.font_container = tk.Frame(self.font_window)
        self.font_container.grid(row=0, column=0)

        self.font_var = tk.StringVar()
        self.style_var = tk.StringVar()
        self.size_var = tk.StringVar()
        self.font_var.set("Arial")
        self.style_var.set("normal")
        self.size_var.set("10")

        self.font_frame = tk.Frame(self.font_container)
        tk.Label(self.font_container, text="Font:").grid(row=0, column=0)
        self.selected_font = tk.Entry(self.font_container, textvariable=self.font_var)
        self.f_scrollbar = tk.Scrollbar(self.font_container, orient=tk.VERTICAL)
        self.fonts_box = tk.Listbox(self.font_container, yscrollcommand=self.f_scrollbar.set)
        self.f_scrollbar.config(command=self.fonts_box.yview)
        self.f_scrollbar.grid(row=1, column=1, rowspan=2, sticky="NS")
        for font in sorted(tk.font.families()):
            if not font.startswith("@"):
                self.fonts_box.insert(tk.END, font)
        self.selected_font.grid(row=1, column=0)
        self.fonts_box.grid(row=2, column=0)
        self.font_frame.grid(row=0, column=0)


        styles = ["normal", "bold", "roman", "italic", "underline", "overstrike"]

        self.style_frame = tk.Frame(self.font_container)
        tk.Label(self.font_container, text="Font style:").grid(row=0, column=2)
        self.selected_style = tk.Entry(self.font_container, textvariable=self.style_var)
        self.st_scrollbar = tk.Scrollbar(self.font_container, orient=tk.VERTICAL)
        self.style_box = tk.Listbox(self.font_container, yscrollcommand=self.st_scrollbar.set)
        self.st_scrollbar.config(command=self.style_box.yview)
        self.st_scrollbar.grid(row=1, column=3, rowspan=2, sticky="NS")
        for style in styles:
            self.style_box.insert(tk.END, style)
        self.selected_style.grid(row=1, column=2, sticky="WE")
        self.style_box.grid(row=2, column=2)
        self.style_frame.grid(row=0, column=1)

        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]

        self.size_frame = tk.Frame(self.font_container)
        tk.Label(self.font_container, text="Size:").grid(row=0, column=4)
        self.selected_size = tk.Entry(self.font_container, textvariable=self.size_var)
        self.s_scrollbar = tk.Scrollbar(self.font_container, orient=tk.VERTICAL)
        self.size_box = tk.Listbox(self.font_container, yscrollcommand=self.s_scrollbar.set)
        self.s_scrollbar.config(command=self.size_box.yview)
        self.s_scrollbar.grid(row=1, column=5, rowspan=2, sticky="NS")
        for size in sizes:
            self.size_box.insert(tk.END, size)
        self.selected_size.grid(row=1, column=4)
        self.size_box.grid(row=2, column=4)
        self.size_frame.grid(row=0, column=2)

        self.sample_actual = tk.Frame(self.font_container, borderwidth=3, width=285, height=80, relief="groove")
        self.sample_lbl = tk.Label(self.sample_actual, text="Sample Text")
        self.sample_lbl.grid(row=0, column=0, sticky="NSEW")
        self.sample_actual.grid(row=3, column=2, columnspan=5, pady=10)
        self.sample_actual.grid_propagate(0)

        self.button_frame = tk.Frame(self.font_container)
        self.confirm_btn = tk.Button(self.button_frame, text="Confirm", command=set_font)
        self.confirm_btn.grid(row=0, column=0, sticky="WE")
        self.cancel_btn = tk.Button(self.button_frame, text="Cancel", command=lambda: self.font_window.destroy())
        self.cancel_btn.grid(row=0, column=1, sticky="WE")
        self.button_frame.grid(row=4, column=4, padx=5, pady=5)

        self.fonts_box.bind("<<ListboxSelect>>", lambda evt, var=self.font_var: onselect(evt, var))
        self.style_box.bind("<<ListboxSelect>>", lambda evt, var=self.style_var: onselect(evt, var))
        self.size_box.bind("<<ListboxSelect>>", lambda evt, var=self.size_var: onselect(evt, var))


if __name__ == "__main__":
    app = Main()
    app.mainloop()
