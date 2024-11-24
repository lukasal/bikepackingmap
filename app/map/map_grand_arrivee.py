import folium
from folium.plugins import BeautifyIcon


def grand_arrivee(activities, settings, final_popup=False):

    grand_arrivee = folium.FeatureGroup(name="Grand arrivee", control=False)

    final_stage = activities[activities.index == max(activities.index)]
    # Finish marker
    icon_ = BeautifyIcon(
        icon="fa fa-flag-checkered",
        icon_shape="circle",
        icon_size=[42, 42],
        icon_anchor=(21, 21),
        inner_icon_style="font-size:30px;",  # Adjust inner icon size
        # border_color='black',
        # text_color="red",
        # background_color='white'
        id="grand_arrivee",
    )

    fm = folium.Marker(
        location=final_stage["map.polyline"][0][-1],
        icon=icon_,
        icon_size=10,
        zIndexOffset=1000,
        tooltip=final_stage["end_location"][0],
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
