import folium
from app.map.map_popup import html_popup


def map_polylines(activities, map_settings):

    polylines = folium.FeatureGroup(name="Polylines", control=False)
    for row in activities.iterrows():
        row_index = row[0]
        row_values = row[1]
        if map_settings.get_interactive_setting("line_stroke"):
            ls = folium.PolyLine(
                row_values["map_polyline"],
                color=map_settings.get_interactive_setting("line_stroke_color"),
                weight=map_settings.get_interactive_setting("line_thickness") + 3,
                # smooth_factor=2
            ).add_to(polylines)
        ls = folium.PolyLine(
            row_values["map_polyline"],
            color=map_settings.get_interactive_setting(
                f"line_color_{row_values['type']}"
            ),
            weight=map_settings.get_interactive_setting("line_thickness"),
            # smooth_factor=2
        )

        # fig = create_elevation_profile(row_values)
        # png = "elevation_profile_.png"
        # fig.savefig(png, dpi=75)
        # plt.close()

        # # read png file
        # elevation_profile = base64.b64encode(open(png, "rb").read()).decode()
        # # delete file
        # os.remove(png)

        # popup text
        popup = html_popup(row_values)

        # add marker to map
        iframe = folium.IFrame(
            popup,
            width=(map_settings.spec_width * map_settings.spec_resolution) + 20,
            height=(map_settings.spec_height * map_settings.spec_resolution) + 20,
        )
        popup = folium.Popup(iframe, max_width=2850)
        ls.add_child(popup)
        ls.add_to(polylines)

    return polylines
