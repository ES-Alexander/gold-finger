#!/usr/bin/env python3

import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

def set_plot_labels(ax, title, ylabel=None, xticks=None):
    if ax is plt:
        ax.title(title)
        if ylabel:
            ax.ylabel(ylabel)
        if xticks:
            ax.xticks(range(len(xticks)), xticks)
    else:
        ax.set_title(title)
        if ylabel:
            ax.set_ylabel(ylabel)
        if xticks:
            ax.set_xticklabels(xticks)

def stacked_column(data, ax, title='title', ylabel='Y', xticks=None,
                   tags=None, relative=False, **kwargs):
    ''' Creates an absolute or relative stacked column graph. '''
    if relative:
        data = data / np.sum([data], axis=2).T
    indices = np.arange(len(data))
    plots = []
    plots.append(ax.bar(indices, data[:,0], **kwargs))
    for col in range(1, len(data[0])):
        plots.append(ax.bar(indices, data[:,col],
                            bottom=data[:,:col].sum(axis=1), **kwargs))

    set_plot_labels(ax, title, ylabel, xticks)
    if tags:
        ax.legend((p[0] for p in plots), tags)

def cumulative_line(data, ax, ylabel='Y', title='title', xticks=None,
                    tags=None, precomputed=False, **kwargs):
    ''' Creates a cumulative line graph for each tag. '''
    indices = np.arange(len(data))
    if not precomputed:
        data = data.copy()
        for timestep in range(1, len(data)):
            data[timestep] += data[timestep-1]

    ax.plot(indices, data)
    set_plot_labels(ax, title, ylabel, xticks)
    if tags:
        ax.legend(tags)

    return data

def pie(data, labels, ax, title='title', autopct='%1.1f%%', **kwargs):
    ''' Creates a pie chart of the given data. '''
    ax.pie(data, labels=tags, autopct=autopct)
    set_plot_labels(ax, title)


# generate data
example_data = np.random.rand(12,3)*100
times = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
tags = ['Groceries', 'PTV', 'Climbing']

# initialise plot settings
time_period = '{}-{}'.format(times[0], times[-1])
abs_title = 'Spending Breakdown ' + time_period
abs_ylabel = 'Amount Spent ($)'
rel_title = 'Relative Spending Breakdown ' + time_period
rel_ylabel = 'Amount Spent (%)'
cum_title = 'Cumulative Breakdown ' + time_period
prop_title = 'Spending Proportions ' + time_period
width = 0.5

# Initialise GUI
root = tkinter.Tk()
root.wm_title("Embedding in Tk")

fig = Figure(figsize=(5, 4), dpi=100)
axs = fig.subplots(2, 2)
stacked_column(example_data, ax=axs[0,0], ylabel=abs_ylabel, title=abs_title,
               xticks=times, tags=tags, width=width)
stacked_column(example_data, ax=axs[0,1], ylabel=rel_ylabel,
               title=rel_title, xticks=times, tags=tags,
               relative=True, width=width)
cum_data = cumulative_line(example_data, ax=axs[1,0], ylabel=abs_ylabel,
                           title=cum_title, xticks=times, tags=tags)[-1]
pie(cum_data, ax=axs[1,1], labels=tags, title=prop_title)


canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


button = tkinter.Button(master=root, text="Quit", command=_quit)
button.pack(side=tkinter.BOTTOM)

tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
