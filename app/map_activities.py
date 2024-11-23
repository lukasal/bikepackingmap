import folium
import folium.plugins as plugins
import time

# color scheme
color = {'Ride':'darkblue', 'Run':'green', 'Hike':'purple'}

tiles = {'stadia_terrain': 'https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=18eb0b62-6b8d-4784-9997-f9b5a9ac39fd',
        'google_hybrid': 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}&apistyle=s.t%3A2|s.e%3Al|p.v%3Aoff',
        'google_satellit': 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&apistyle=s.t%3A2|s.e%3Al|p.v%3Aoff'}

def centroid(polylines):
    x, y = [], []
    for polyline in polylines:
        for coord in polyline:
            x.append(coord[0])
            y.append(coord[1])
    return [(min(x)+max(x))/2, (min(y)+max(y))/2]

def bounding_box(polylines, margin = 0.3):
    x, y = [], []
    for polyline in polylines:
        for coord in polyline:
            x.append(coord[0])
            y.append(coord[1])
    return [[min(x)- margin,min(y)-margin], [max(x)+ margin,max(y)+ margin]]


# plot all activities on map
def map_activities(activities, 
                  out_file = 'mymap_terrain.html', 
                  tiles_name = 'stadia_terrain',
                  final_popup = False,
                  dynamic_tiles = True,
                  zoom_margin = 0.05):
    resolution, width, height = 75, 6, 6.5

    m = folium.Map(location=centroid(activities['map.polyline']),
                   width= 2560,
                   height = 1740,
                   zoom_start= 6, 
                   tiles = None,
                   attr= ".",
                   )

    folium.TileLayer(tiles[tiles_name], show=True, attr = tiles_name, name = tiles_name).add_to(m)
    if dynamic_tiles:
        for tile_name, tile_path in tiles.items():
            folium.TileLayer(tile_path, attr = tile_name, name = tile_name, show=False).add_to(m)

        folium.LayerControl().add_to(m)

    for row in activities.iterrows():
        row_index = row[0]
        row_values = row[1]
        ls = folium.PolyLine(row_values['map.polyline'], color='white',
                                 weight=8,     
                                 #smooth_factor=2
                                ).add_to(m)
        ls = folium.PolyLine(row_values['map.polyline'], color=color[row_values['type']],
                             weight=5,     
                             #smooth_factor=2
                            ).add_to(m)

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
        iframe = folium.IFrame(html, width=(width*resolution)+20, height=(height*resolution)+20)
        popup = folium.Popup(iframe, max_width=2850)
        ls.add_child(popup)
        ls.add_to(m)

    # House Markler for each stage town:
    # stage_town_activities = activities[activities['type'] == "Ride"].groupby(activities[activities['type'] == "Ride"].index.date).apply(lambda x: x.loc[x.index.min()])
    stage_town_activities = activities.groupby(activities.index.date).apply(lambda x: x.loc[x.index.min()])
    for row in stage_town_activities.iterrows():
        row_values = row[1]
        # color
        # #if row_values['restday_previous'] == 0:#
        icon_color = "#007799" 
        # else:
        #     icon_color = "orange"

        icon_=plugins.BeautifyIcon(
                         icon="house",
                         icon_shape="circle",
                         border_color='black',
                         text_color=icon_color,
                     background_color='white'
                 )
        folium.Marker(location=row_values['map.polyline'][0],
                  icon=icon_,
                  icon_size = 10,
                  tooltip = row_values['start_location']).add_to(m)
        icon_=plugins.BeautifyIcon(
                         icon="play",
                         icon_shape="circle",
                         border_color='black',
                         text_color="green",
                         background_color='white'
                     )

    # Grand depart marker
    icon_=plugins.BeautifyIcon(
                         icon="play",
                         icon_shape="circle",
                         border_color='black',
                         text_color="green",
                         background_color='white',
                         icon_size=[42, 42],
                         icon_anchor=(21, 21),
                         inner_icon_style='font-size:30px;'  # Adjust inner icon size
                     )

    folium.Marker(location=activities[activities.index == min(activities.index)]['map.polyline'][0][0],
                  icon=icon_,
                  icon_size = 10,
                  zIndexOffset = 1000,
                  tooltip = activities[activities.index == min(activities.index)]['start_location'][0]).add_to(m)
    # Finish marker
    icon_=plugins.BeautifyIcon(
                         icon="fa fa-flag-checkered",
                         icon_shape="circle",
                         icon_size=[42, 42],
                         icon_anchor=(21, 21),
                         inner_icon_style='font-size:30px;'  # Adjust inner icon size
                         #border_color='black',
                         #text_color="red",
                         #background_color='white'
    )

    fm = folium.Marker(location=stage_town_activities[stage_town_activities.index == max(stage_town_activities.index)]['map.polyline'][0][-1], 
                  icon=icon_, 
                  icon_size = 10,
                  zIndexOffset = 1000,
                  tooltip = stage_town_activities[stage_town_activities.index == max(stage_town_activities.index)]['end_location'][0]
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
    #     iframe = folium.IFrame(html, width=(width*resolution)+20, height=(height*resolution)+20)
    #     popup = folium.Popup(iframe, max_width=8850)
    #     fm.add_child(popup)
    fm.add_to(m)

    m.fit_bounds(bounding_box(activities['map.polyline'], margin = zoom_margin)) 

    m.save(out_file)
    # display(m)
