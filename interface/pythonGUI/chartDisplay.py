# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:52:23 2023

@author: Santosh Bag
"""

import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# create a pandas DataFrame of stock prices
data = {'Date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04'],
        'Price': [100, 110, 120, 115]}
df = pd.DataFrame(data)

# define a function to display the stock price chart
def display_chart():
    # create the main window
    root = tk.Tk()
    root.title("Stock Price Chart")

    # create a figure and axis for the chart
    fig, ax = plt.subplots()

    # plot the stock price data
    ax.plot(df['Date'], df['Price'])

    # create a canvas widget to display the chart
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()

    # pack the canvas widget
    canvas.get_tk_widget().pack()

    # start the main loop
    root.mainloop()

# create the main window
root = tk.Tk()
root.title("Button Example")

# create a button to display the stock price chart
display_button = tk.Button(root, text="Display Stock Price Chart", command=display_chart)
display_button.pack()

# start the main loop
root.mainloop()
