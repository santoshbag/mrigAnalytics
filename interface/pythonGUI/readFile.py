# -*- coding: utf-8 -*-
"""
Created on Tue May  2 13:03:59 2023

@author: Santosh Bag
"""

import tkinter as tk
from tkinter import filedialog
import pandas as pd

# define a function to display the contents of the selected file
def display_contents():
    # open a file dialog to select a CSV file
    filename = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])

    # read the CSV file into a pandas DataFrame
    df = pd.read_csv(filename)

    # create a new window to display the DataFrame
    window = tk.Toplevel(root)
    window.title("CSV File Contents")

    # create a table to display the DataFrame
    table = tk.Text(window)
    table.pack()

    # insert the contents of the DataFrame into the table
    table.insert(tk.END, df.to_string())

# create the main window
root = tk.Tk()
root.title("CSV File Viewer")

# create a button to select a file and display its contents
select_button = tk.Button(root, text="Select File", command=display_contents)
select_button.pack()

# start the main loop
root.mainloop()
