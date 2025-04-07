import folium
from folium.plugins import BeautifyIcon
import numpy as np

def map_grand_arrivee(activities, settings, final_popup=False):

    grand_arrivee = folium.FeatureGroup(name="Grand arrivee", control=False)
    # No final stage via date - no marker

    # if activities["end_date"].max() is np.nan:
    #     # return grand_arrivee
    final_stage = activities.iloc[[-1]]
    # else:
    #     final_stage = activities[activities["end_date"] == activities["end_date"].max()]

    # Finish marker
    icon_ = BeautifyIcon(
        icon=settings.get_interactive_setting("arrivee_icon"),
        icon_shape=settings.get_interactive_setting("arrivee_icon_shape"),
        border_color=(
            "transparent"
            if settings.get_interactive_setting("arrivee_border_transparent")
            else settings.get_interactive_setting("arrivee_border_color")
        ),
        text_color=settings.get_interactive_setting("arrivee_symbol_color"),
        background_color=(
            "transparent"
            if settings.get_interactive_setting("arrivee_background_transparent")
            else settings.get_interactive_setting("arrivee_background_color")
        ),
        icon_size=[
            settings.get_interactive_setting("arrivee_icon_size"),
            settings.get_interactive_setting("arrivee_icon_size"),
        ],
        icon_anchor=(
            int(settings.get_interactive_setting("arrivee_icon_size")) / 2,
            int(settings.get_interactive_setting("arrivee_icon_size")) / 2,
        ),
        inner_icon_style=f"font-size:{settings.get_interactive_setting('arrivee_icon_inner_size')}px;",  # Adjust inner icon size
        id="grand_arrivee",
    )

    fm = folium.Marker(
        location=final_stage["end_latlng"].iloc[0],
        icon=icon_,
        icon_size=10,
        zIndexOffset=1000,
        tooltip=final_stage["end_location"].iloc[0],
    )
    # final popup
    # if final_popup:
    #     png = 'total_elevation_profile.png'
    #     #fig = create_total_elevation(ride_activities)
    #     fig.savefig(png, dpi=75)
    #     plt.close()

    #     # read png file
    #     total_elevation_profile = base64.b64encode(open(png, 'rb').read()).decode()

    #     # delete file
    #     os.remove(png)

    #     # popup text
    #     html = """
    #         <h3>Palermo - Freiburg</h3>
    #             <h4>Radstatistiken</h4>
    #             <p>
    #                 <code>
    #                 Distanz&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:&nbsp;{:.2f} Km<br>
    #                 Fahrzeit&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {} <br>
    #                 &#8960 Geschwindigkeit&nbsp;: {:.2f} km/h<br>
    #                 Höhenmeter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:&nbsp;{} m
    #                 </code>
    #             </p>
    #             <h4>Laufstatistiken</h4>
    #             <p>
    #                 <code>
    #                 Distanz&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:&nbsp;{:.2f} Km<br>
    #                 Zeit&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {} <br>
    #                 Höhenmeter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:&nbsp;{} m
    #                 </code>
    #             </p>
    #         <img src="data:image/png;base64,{}">
    #         """.format(
    #             summary_stats_ride['distance'],
    #             print_moving_time(summary_stats_ride['moving_time']),
    #             summary_stats_ride['speed'],
    #             summary_stats_ride['total_elevation_gain'],
    #             summary_stats_hike['distance'],
    #             print_moving_time(summary_stats_hike['moving_time']),
    #             #summary_stats_ride['speed'],
    #             summary_stats_hike['total_elevation_gain'],
    #             total_elevation_profile
    #         )

    #         # add marker to map
    #     iframe = folium.IFrame(html, width=(width*self.spec_resolution)+20, height=(height*self.spec_resolution)+20)
    #     popup = folium.Popup(iframe, max_width=8850)
    #     fm.add_child(popup)
    fm.add_to(grand_arrivee)

    return grand_arrivee
