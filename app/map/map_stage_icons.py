import folium
from folium.plugins import BeautifyIcon


def map_stage_icons(activities, settings):
    # House Markler for each stage town:
    stage_icons = folium.FeatureGroup(name="Stage Icons", control=False)

    # stage_town_activities = activities[activities['type'] == "Ride"].groupby(activities[activities['type'] == "Ride"].index.date).apply(lambda x: x.loc[x.index.min()])

    stage_town_activities = activities.loc[
        activities.groupby("date")["end_date"].idxmax()
    ]

    for row in stage_town_activities.iterrows():
        row_values = row[1]
        # color
        # #if row_values['restday_previous'] == 0:#
        # icon_color = "#007799"
        # else:
        #     icon_color = "orange"

        icon_ = BeautifyIcon(
            icon=settings.get_interactive_setting("stage_start_icon"),
            icon_shape=settings.get_interactive_setting("stage_icon_shape"),
            border_color=(
                "transparent"
                if settings.get_interactive_setting("stage_border_transparent")
                else settings.get_interactive_setting("stage_border_color")
            ),
            text_color=settings.get_interactive_setting("stage_symbol_color"),
            background_color=(
                "transparent"
                if settings.get_interactive_setting("stage_background_transparent")
                else settings.get_interactive_setting("stage_background_color")
            ),
            icon_size=[
                settings.get_interactive_setting("stage_icon_size"),
                settings.get_interactive_setting("stage_icon_size"),
            ],
            icon_anchor=(
                int(settings.get_interactive_setting("stage_icon_size")) / 2,
                int(settings.get_interactive_setting("stage_icon_size")) / 2,
            ),
            inner_icon_style=f"font-size:{settings.get_interactive_setting('stage_icon_inner_size')}px;",  # Adjust inner icon size
        )
        folium.Marker(
            location=row_values["end_latlng"],
            icon=icon_,
            icon_size=10,
            tooltip=row_values["end_location"],
        ).add_to(stage_icons)

    return stage_icons
