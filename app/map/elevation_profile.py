import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import base64
import os


def up_gen(low, up):
    value = low
    while True:
        if value > up:
            value = low
        yield value
        value += 1


# references = pd.DataFrame({'dist' : [18,60,75, 125], 'loc' : ['Albulapass', 'Lenzerheide', 'Chur', 'Walensee']})
def create_elevation_profile(
    map_distance,
    map_elevation,
    reference_labels=pd.DataFrame(columns=["reference_dist", "reference_name"]),
    background_color="white",
    size=(5.8, 3),
    top_highlight=True,
):
    fig, ax = plt.subplots(figsize=size, tight_layout=True)

    x = pd.Series(map_distance)
    x_max = np.nanmax(x)
    y_min = np.nanmin(map_elevation)
    y_max = np.nanmax(map_elevation)
    y_min_plot = y_min - 50
    y_max_plot = max(y_max + 100, y_min + 500)
    y_range = y_max_plot - y_min_plot

    y = pd.Series(map_elevation).rolling(30).mean()
    # ax1.plot(pd.Series(my_ride['map_distance'])/1000, y, lw=2)
    if top_highlight:
        ax.plot(x, y, lw=2, c="#1a1a1a")
    ax.fill_between(x, y_min_plot, y, alpha=1, fc="darkgrey", xunits="km")

    ax.grid(axis="y", color="lightgrey", alpha=1)

    ax.label_outer()
    ax.margins(x=0)

    ax.set_axisbelow(True)

    # create vertical referrence lines

    max_height = 0
    random_move = up_gen(0, 2)

    for index, row in reference_labels.iterrows():
        height = (
            pd.Series(map_elevation)[
                (pd.Series(map_distance)).between(
                    row["reference_dist"] - 20,
                    row["reference_dist"] + 20,
                    inclusive="both",
                )
            ].max()
            + 200
            + y_range / 7 * next(random_move)
        )
        ax.vlines(
            x=row["reference_dist"],
            ymin=y_min_plot,
            ymax=height,
            linewidth=1,
            color="black",
            linestyles="dashed",
            alpha=0.9,
        )

        if row["reference_dist"] < x_max / 10:
            h_alignment = "left"
        elif row["reference_dist"] > x_max * 9 / 10:
            h_alignment = "right"
        else:
            h_alignment = "center"
        plt.text(
            row["reference_dist"],
            height + y_range / 20,
            row["reference_label"],
            fontsize=9,
            horizontalalignment=h_alignment,
            verticalalignment="bottom",
            alpha=0.9,
        )
        if height > max_height:
            max_height = height

    ax.set_ylim(y_min_plot, max(y_max_plot, max_height + y_range / 4))
    xlabels = ["{:,.0f}".format(x) + " Km" for x in ax.get_xticks()]
    ax.set_xticklabels(xlabels)

    ax.set_ylabel("Altitude [m]", fontsize=12)
    ax.set_facecolor(background_color)
    fig.patch.set_facecolor(background_color)

    fig.suptitle("Altitude profile")
    return fig


def create_binary_elevation_profile(*args, **kwargs):
    fig = create_elevation_profile(
        *args,
        **kwargs,
    )
    png = "elevation_profile_.png"
    fig.savefig(png, dpi=75)
    plt.close()

    # read png file
    elevation_profile = base64.b64encode(open(png, "rb").read()).decode()
    # delete file
    os.remove(png)
    return elevation_profile
