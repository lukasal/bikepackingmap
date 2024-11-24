import folium
from folium.plugins import BeautifyIcon


def map_stage_icons(activities, settings):
    # House Markler for each stage town:
    stage_icons = folium.FeatureGroup(name="Stage Icons", control=False)

    # stage_town_activities = activities[activities['type'] == "Ride"].groupby(activities[activities['type'] == "Ride"].index.date).apply(lambda x: x.loc[x.index.min()])
    stage_town_activities = activities.groupby(activities.index.date).apply(
        lambda x: x.loc[x.index.min()]
    )
    if settings.stage_labels_active:

        for row in stage_town_activities.iterrows():
            row_values = row[1]
            # color
            # #if row_values['restday_previous'] == 0:#
            # icon_color = "#007799"
            # else:
            #     icon_color = "orange"

            icon_ = BeautifyIcon(
                icon=settings.stage_start_icon,
                icon_shape=settings.stage_icon_shape,
                border_color=settings.stage_border_color,
                text_color=settings.stage_start_color,
                background_color=settings.stage_background_color,
            )
            folium.Marker(
                location=row_values["map.polyline"][0],
                icon=icon_,
                icon_size=10,
                tooltip=row_values["start_location"],
            ).add_to(stage_icons)

    return stage_icons
