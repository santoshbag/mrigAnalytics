# -*- coding: utf-8 -*-
"""
Created on Tue May  2 13:53:51 2023

@author: Santosh Bag
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd

# create a pandas DataFrame
data = {'Name': ['John', 'Jane', 'Bob', 'Alice'],
        'Age': [25, 32, 42, 28],
        'Gender': ['M', 'F', 'M', 'F']}
df = pd.DataFrame(data)

# define a function to display the DataFrame
def display_dataframe():
    # create the main window
    root = tk.Tk()
    root.title("DataFrame Example")

    # create a treeview widget to display the DataFrame
    tree = ttk.Treeview(root, columns=list(df.columns), show="headings")
    for col in df.columns:
        tree.heading(col, text=col)

    # add the data to the table
    for i, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # pack the treeview widget
    tree.pack()

    # start the main loop
    root.mainloop()

# create the main window
root = tk.Tk()
root.title("Button Example")

# create a button to display the DataFrame
display_button = tk.Button(root, text="Display DataFrame", command=display_dataframe)
display_button.pack()

# start the main loop
root.mainloop()
