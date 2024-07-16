import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

colors_bathymetry = [
                "#3ba0f5",
                "#72bbf7",
                "#7ec0f7",
                "#91cdff",
                "#a4d0f5",
                "#aed5f5",
                "#badbf7",
                "#c8e3fa",
                "#d6ecff",
                "#def0ff",
                "#18a315",
                "#49fa46",
                "#94ff6e",
                "#b1ff6e",
                "#e7ff6e",
                "#ffec6e",
                "#ffd36e",
            ]

colors_bathymetry2 = [
                "midnightblue",     #-1000
                "navy",             #-500
                "darkblue",         #-100
                "mediumblue",       #-80
                "blue",             #-60
                "steelblue",        #-50
                "dodgerblue",       #-40
                "deepskyblue",      #-30
                "darkturquoise",    #-20
                "aqua",             #-10
                "aliceblue",        #0
                "palegreen",        #10
                "forestgreen",      #20
                "navajowhite",      #50
                "sandybrown",       #100
                "coral",            #500
                "indianred",        #1000
            ]

colors = [ "#1A6AD0", "#3D98E3", "#79C4E9", "#055A05", "#99C48C", "#AC8C1A"]
values = [ -1800 , -1200, -0.01, 0, 600 , 1200 ]


# Function to convert RGB to grayscale
def rgb_to_gray(rgb):
    r, g, b = rgb
    gray_value = 0.299 * r + 0.587 * g + 0.114 * b
    return (np.array([0.299 * r, 0.587 * g, 0.114 * b]))

    # return gray_value / 255.0  # Normalize to [0, 1]



def colors_plotter(colors):
    """Plots a horizontal box with n divisions for n colors provided.
    Each one containing the color given.

    --------
    Parameters
    ----------
    colors: list
        List of colors to be plotted
    
    Returns
    -------
    None:
        but plots an image
    
    """
    n = len(colors)

    fig, ax = plt.subplots(figsize=(8, 2))  # You can adjust the figsize as needed

    # Create a horizontal bar for each division
    for i in range(n):
        ax.barh(0, 1, color=colors[i], left=i, align='edge')

    ax.set_yticks([])
    ax.set_yticklabels([])

    ax.set_xlim(0, n)
    ax.set_xticks([])
    ax.set_xticklabels([])

    for i in range(n):
        ax.text(i + 0.5, 0.2, f'Color {i + 1}', ha='left', va='bottom', fontsize=12, color='black', rotation=90)

    ax.set_title('Colors Chosen')
    plt.show()

# colors_plotter(colors_bathymetry)



"""
fig = plt.figure( figsize=(2,4) )
ax = fig.add_axes([0, 0.05, 0.25, 0.9])

norm = mpl.colors.Normalize(vmin=min(values), vmax=max(values))  
normed_vals = norm(values)

cmap = LinearSegmentedColormap.from_list("mypalette", list(zip(normed_vals, colors)), N=1000)  
cb = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='vertical')

plt.show()
"""