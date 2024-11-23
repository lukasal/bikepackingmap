import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
color = {'Ride':'darkblue', 'Run':'green', 'Hike':'purple'}


def up_gen(low, up):
    value = low
    while True:
        if value > up:
            value = low
        yield value
        value += 1 


# references = pd.DataFrame({'dist' : [18,60,75, 125], 'loc' : ['Albulapass', 'Lenzerheide', 'Chur', 'Walensee']})
def create_elevation_profile(
    my_ride, background_color="white", size=(5.8, 3), top_color=True
):
    fig, ax = plt.subplots(figsize=size, tight_layout=True)

    x = pd.Series(my_ride['map.distance'])/1000
    x_max = np.nanmax(x)
    y_min = np.nanmin(my_ride['map.elevation'])
    y_max = np.nanmax(my_ride['map.elevation'])
    y_min_plot = y_min-50
    y_max_plot = max(y_max+100,y_min + 500)
    y_range = y_max_plot-y_min_plot

    y = pd.Series(my_ride['map.elevation']).rolling(30).mean()
    # ax1.plot(pd.Series(my_ride['map.distance'])/1000, y, lw=2)
    if top_color:
        ax.plot(x, y, lw=2, c=color[my_ride['type']])
    ax.fill_between(x, y_min_plot, y, alpha=1, fc='darkgrey', xunits="km")

    ax.grid(axis='y',color='lightgrey', alpha = 1)

    ax.label_outer()
    ax.margins(x=0)

    ax.set_axisbelow(True)

    # create vertical referrence lines
    references = pd.DataFrame({'reference_dist':my_ride.get('reference_dist', default=[]), 'reference_label':my_ride.get('reference_label', default=[])})
    max_height= 0
    random_move = up_gen(0,2)

    for index, row in references.iterrows():
        height = pd.Series(my_ride['map.elevation'])[(pd.Series(my_ride['map.distance'])/1000).between(row['reference_dist']-20, row['reference_dist']+20, inclusive='both')].max() + 200 + y_range/7 * next(random_move) 
        ax.vlines(x=row['reference_dist'], ymin=y_min_plot, ymax=height, linewidth=1, color='black', linestyles= 'dashed', alpha = 0.9)

        if row['reference_dist'] <  x_max/10:
            h_alignment = 'left'
        elif row['reference_dist'] >  x_max*9/10:
            h_alignment = 'right'
        else:
            h_alignment = 'center'    
        plt.text(row['reference_dist'], height+y_range/20, row['reference_label'], fontsize = 9,horizontalalignment=h_alignment,
            verticalalignment='bottom', alpha = 0.9)    
        if height > max_height:
            max_height = height

    ax.set_ylim(y_min_plot, max(y_max_plot, max_height+y_range/4))
    xlabels = ['{:,.0f}'.format(x) + ' Km' for x in ax.get_xticks()]
    ax.set_xticklabels(xlabels)

    ax.set_ylabel('Höhe')
    ax.set_facecolor(background_color)
    fig.patch.set_facecolor(background_color)

    fig.suptitle('Höhenprofil')
    return fig
