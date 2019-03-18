import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk, messagebox, filedialog, font
from os.path import basename, dirname, realpath, join
from string import whitespace

from jnlogic import File


class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.wm_geometry("800x600")
        self.curr_file = None
        
        self.text_entry = tkst.ScrolledText()
        
        self.menu = MenuBar(self)
        self.config(menu=self.menu) 
        
        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")
        
        self.status_bar = StatusBar(self)      
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.menu.new_file(self)
        
        self.text_entry.bind("<Enter>", lambda evt, master=self: self.menu.set_button_state(evt, master))
        self.text_entry.bind("<Leave>", lambda evt, master=self: self.menu.set_button_state(evt, master))
        self.text_entry.bind("<<Modified>>", lambda evt, master=self: self.menu.set_button_state(evt, master))
        
        self.bind_all("<Control-a>", lambda evt, master=self: self.menu.select_all(master))
        self.bind_all("<Control-s>", lambda evt, master=self: self.menu.save_file(master))
        self.bind_all("<Control-n>", lambda evt, master=self: self.menu.new_file(master))
        self.bind_all("<Control-o>", lambda evt, master=self: self.menu.open_file(master))
        
    def setup(self):
        """
        Currently this only sets the title for the window.
        Planned to do more later.
        """
        self.title("jNote - " + self.curr_file.file_name)

        
class MenuBar(tk.Menu):

    def __init__(self, master):
        tk.Menu.__init__(self, master)

        self.wrap_var = tk.StringVar()
        self.wrap_var.set("none")
        
        self.file_menu = tk.Menu(self, tearoff=False)
        self.file_menu.add_command(label="New", command=lambda: self.new_file(master), accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=lambda: self.open_file(master), accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=lambda: self.save_file(master), accelerator="Ctrl+S", state="disabled")
        self.file_menu.add_command(label="Save As...", command=lambda: self.saveas_file(master))
        self.file_menu.add_separator()
        self.file_menu.add_cascade(label="Quit", command=lambda: master.destroy())
        self.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = tk.Menu(self, tearoff=False)
        self.edit_menu.add_command(label="Undo", command=lambda master=master: self.undo(master), accelerator="Ctrl+Z", state="disabled")
        self.edit_menu.add_command(label="Redo", command=lambda master=master: self.redo(master), accelerator="Ctrl+R", state="disabled")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=lambda master=master: self.cut(master), accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=lambda master=master: self.copy(master), accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=lambda master=master: self.paste(master), accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All", command=lambda master=master: self.select_all(master), accelerator="Ctrl+A", state="disabled")
        self.add_cascade(label="Edit", menu=self.edit_menu)

        self.format_menu = tk.Menu(self, tearoff=False)
        self.format_menu.add_checkbutton(label="Word Wrap", command=lambda master=master: self.toggle_wrap(master))
        self.format_menu.add_command(label="Font", command=lambda master=master: self.open_font_window(master))
        self.add_cascade(label="Format", menu=self.format_menu)

        self.help_menu = tk.Menu(self, tearoff=False)
        self.help_menu.add_command(label="Help [coming soon]")
        self.help_menu.add_command(label="About jNotes [coming soon]")
        self.add_cascade(label="Help", menu=self.help_menu)     
                
    def set_button_state(self, evt, master): 
        """
        Enables/disables the save, undo, redo, and select all menu options
        based on whether or not they can actually be used.
        """
        if master.text_entry.edit_modified():
            self.file_menu.entryconfig(2, state="normal")
            self.edit_menu.entryconfig(0, state="normal")
        else:
            self.file_menu.entryconfig(2, state="disabled")
            self.edit_menu.entryconfig(0, state="disabled")
        
        if len(master.text_entry.get("1.0", tk.END)) > 1:
            self.edit_menu.entryconfig(7, state="normal")

        else:
            self.edit_menu.entryconfig(7, state="disabled")        
                    
    def add_scrolledtext(self, master):
        """
        Adds the scrolledtext box to the container frame.
        """
        if master.text_entry and self.master.text_entry.winfo_exists():
            master.container.destroy()
        master.container = tk.Frame(master)
        master.container.pack(expand=True, fill="both")
        master.text_entry = tkst.ScrolledText(master.container, wrap=self.wrap_var.get(), undo=True, maxundo=-1)
        master.text_entry.pack(expand=True, fill="both")

    def new_file(self, master):
        """
        Creates a new file object.  Then clears container frame and creates a
        new one by calling 'add_scrolledtext'.
        """
        self.master.curr_file = File(join(dirname(realpath(__file__)) + "\\New File.txt"))
        self.add_scrolledtext(master)
        master.setup()

    def open_file(self, master):
        """
        Destroys container frame and creates a new one by calling
        'add_scrolledtext'.  Inserts the data of that file into
        the newly created scrolledtext box.  Then creates a new File
        object and sets the curr_file to that object.
        """
        file_to_open = filedialog.askopenfilename(defaultextension = "txt",
                                                  initialdir = master.curr_file.file_path,
                                                  filetypes=(("Text files", "*.txt"),
                                                  ("All files", "*.*"))
                                                 )
        if file_to_open:
            with open(file_to_open, "r") as f:
                data = f.read()
            master.curr_file = File(file_to_open)
            self.add_scrolledtext(master)
            master.text_entry.insert("1.0", data)
            master.text_entry.edit_modified(False)
            master.setup()

    def save_file(self, master):
        """
        Writes text to file and sets saved flag for curr_file to true.
        """
        if master.menu.file_menu.entrycget(2, "state") == "normal":
            with open(master.curr_file.file_path, "w+") as f:
                f.write(master.text_entry.get("1.0", "end-1c"))
                master.curr_file.saved = True
                master.text_entry.edit_modified(False)
                master.setup()
        else:
            self.saveas_file(master)

    def saveas_file(self, master):
        """
        Opens file dialog for user to save new file.
        """
        data = master.text_entry.get("1.0", "end-1c")
        save_location = filedialog.asksaveasfilename(defaultextension = "txt",
                                                     initialdir = master.curr_file.file_path,
                                                     filetypes=(("Text files", "*.txt"),
                                                     ("All files", "*.*"))
                                                    )
        if save_location:
            with open(save_location, "w+") as f:
                f.write(data)
            master.curr_file = File(save_location)
            master.curr_file.saved = True
            master.text_entry.edit_modified(False)
            master.setup()

    def undo(self, master):
        try:
            master.text_entry.edit_undo()
            self.edit_menu.entryconfig(1, state="normal")
        except tk.TclError:
            self.edit_menu.entryconfig(0, state="disabled")

    def redo(self, master):
        try:
            master.text_entry.edit_redo()
        except tk.TclError:
            self.edit_menu.entryconfig(1, state="disabled")

    def cut(self, master):
        master.text_entry.event_generate("<<Cut>>")
        
    def copy(self, master):
        master.text_entry.event_generate("<<Copy>>")

    def paste(self, master):
        master.text_entry.event_generate("<<Paste>>")

    def select_all(self, master):
        master.text_entry.tag_add("sel",'1.0','end')

    def toggle_wrap(self, master):
        if self.wrap_var.get() == "word":
            self.wrap_var.set("none")
        else:
            self.wrap_var.set("word")
            
        master.text_entry.config(wrap=self.wrap_var.get())
            
        
    def open_font_window(self, master):
        """
        Opens a new window which allows the user to change the font
        of the scrolledtext widget.
        """
        self.font_popup = FontWindow(master)
       
        
class StatusBar(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        
        self.columnconfigure(0, weight=1)
        self.status_frame = tk.Frame(self, relief=tk.SUNKEN, bd=1)
        self.status_frame.grid(column=0, row=0, sticky="ew")
        
        tk.Label(self.status_frame, text="Charcter Count: ", anchor="e").grid(column=1, row=0, sticky="e")
        self.char_count = tk.StringVar()
        self.char_count.set("0")
        tk.Label(self.status_frame, textvariable=self.char_count).grid(column=2, row=0, sticky="e")

        tk.Label(self.status_frame, text="Ln: ").grid(column=3, row=0, sticky="e")
        self.curr_line = tk.StringVar()
        self.curr_line.set("1")
        tk.Label(self.status_frame, textvariable=self.curr_line).grid(column=4, row=0, sticky="e")
        
        tk.Label(self.status_frame, text="Col: ").grid(column=5, row=0, sticky="e")
        self.curr_col = tk.StringVar()
        self.curr_col.set("1")
        tk.Label(self.status_frame, textvariable=self.curr_col).grid(column=6, row=0, sticky="e")
        
        master.text_entry.bind_all("<Key>", lambda evt, master=master: self.update_status(evt, master))
        
    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

    def update_status(self, evt, master):
        self.position = master.text_entry.index(tk.INSERT).split(".")
        self.char_count.set(len(master.text_entry.get("1.0", tk.END)) - 1)
        self.curr_line.set(self.position[0])
        self.curr_col.set(self.position[1])

        

class FontWindow(tk.Toplevel):
    
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)

        self.title("Font")
        self.resizable(0, 0)

        self.font_container = tk.Frame(self)
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


        styles = ["normal", "bold", "italic", "underline", "overstrike"]

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

        self.sample_frame = tk.Frame(self.font_container, borderwidth=3, width=285, height=80, relief="groove")
        self.sample_lbl = tk.Label(self.sample_frame, text="Sample Text", anchor="center")
        self.sample_lbl.grid(row=0, column=0, sticky="NSEW")
        self.sample_frame.grid(row=3, column=2, columnspan=5, pady=10)
        self.sample_frame.grid_propagate(0)

        self.button_frame = tk.Frame(self.font_container)
        self.confirm_btn = tk.Button(self.button_frame, text="Confirm", command=lambda master=master: self.set_font(master))
        self.confirm_btn.grid(row=0, column=0, sticky="WE")
        self.cancel_btn = tk.Button(self.button_frame, text="Cancel", command=lambda: self.destroy())
        self.cancel_btn.grid(row=0, column=1, sticky="WE")
        self.button_frame.grid(row=4, column=4, padx=5, pady=5)

        self.fonts_box.bind("<<ListboxSelect>>", lambda evt, var=self.font_var: self.onselect(evt, var))
        self.style_box.bind("<<ListboxSelect>>", lambda evt, var=self.style_var: self.onselect(evt, var))
        self.size_box.bind("<<ListboxSelect>>", lambda evt, var=self.size_var: self.onselect(evt, var))
        
    def onselect(self, evt, var):
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

    def set_font(self, master):
        """
        Sets the font, style, and size of the scrolledtext field.
        """
        master.text_entry.config(font=(self.font_var.get(), self.size_var.get(), self.style_var.get()))
        self.destroy()

        
class AboutWindow(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        
        tk.Label(text="jNote", font="bold").grid(column=0, row=0)

if __name__ == "__main__":
    app = Main()
    app.mainloop()
