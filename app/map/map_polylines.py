import folium
import time


def map_polylines(activities, map_settings):

    polylines = folium.FeatureGroup(name="Polylines", control=False)
    for row in activities.iterrows():
        row_index = row[0]
        row_values = row[1]
        ls = folium.PolyLine(
            row_values["map.polyline"],
            color="white",
            weight=map_settings.line_thickness + 3,
            # smooth_factor=2
        ).add_to(polylines)
        ls = folium.PolyLine(
            row_values["map.polyline"],
            color=map_settings.color[row_values["type"]],
            weight=map_settings.line_thickness,
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
        html = """
                <h3>{}</h3>
                    <p>
                        <code>
                        Datum &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {} <br>
                        Uhrzeit am Start : {}
                        </code>
                    </p>
                <h4>{}</h4>
                    <p> 
                        <code>
                            Distanz&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp: {:.2f} km <br>
                            Höhenmeter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp: {:.0f} m <br>
                            Bewegungszeit&nbsp;&nbsp;&nbsp;&nbsp;&nbsp: {} <br>
                            Verstrichene Zeit : {} <br>
                            &#8960 Geschwindigkeit : {:.2f} km/h (maximum: {:.2f} km/h) <br>
                            &#8960 Herzfrequenz&nbsp;&nbsp&nbsp;&nbsp;: {:.0f} bpm (maximum: {:.0f} bpm) <br>
                            &#8960 Temperature&nbsp&nbsp;&nbsp;&nbsp;&nbsp;: {:.1f} <br>
                        </code>
                    <img src="data:image/png;base64,{}">
                    </p>
            
                """.format(
            row_values["name"],
            row_index.date(),
            row_index.time(),
            row_values["type"],
            row_values["distance"],
            row_values["total_elevation_gain"],
            time.strftime("%H:%M:%S", time.gmtime(row_values["moving_time"])),
            time.strftime("%H:%M:%S", time.gmtime(row_values["elapsed_time"])),
            row_values["average_speed"],
            row_values["max_speed"],
            row_values["average_heartrate"],
            row_values["max_heartrate"],
            row_values["average_temp"],
            row_values["elevation_profile"],
        )

        # add marker to map
        iframe = folium.IFrame(
            html,
            width=(map_settings.spec_width * map_settings.spec_resolution) + 20,
            height=(map_settings.spec_height * map_settings.spec_resolution) + 20,
        )
        popup = folium.Popup(iframe, max_width=2850)
        ls.add_child(popup)
        ls.add_to(polylines)

    return polylines
