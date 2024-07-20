from tkinter import filedialog
import tkinter as tk


def browse(text, filetypes):
    file_path = filedialog.askopenfilename(
        filetypes=filetypes
    )
    if file_path:
        text.delete(0, tk.END)
        text.insert(0, file_path)
        text.xview(tk.END)


def java_browse(text, display, unbind, bind):
    file_path = filedialog.askopenfilename(
        filetypes=[("Java files", "*.java")]
    )
    if file_path:
        unbind()

        fill_java_src_window(file_path, display)

        text.delete(0, tk.END)
        text.insert(0, file_path)
        text.xview(tk.END)

        bind()


def fill_java_src_window(path, display):
    try:
        with open(path, "r") as file:
            data = file.read()

        display.delete("0.0", "end")
        display.insert("0.0", data)
    except Exception as e:
        return
