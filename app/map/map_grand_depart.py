import folium
from folium.plugins import BeautifyIcon
import numpy as np

def map_grand_depart(activities, settings):

    grand_depart = folium.FeatureGroup(name="Grand depart", control=False)

    if activities["start_date"].min() is np.nan:
        # return grand_arrivee
        first_stage = activities.iloc[[0]]
    else:
        first_stage = activities[
            activities["start_date"] == activities["start_date"].min()
        ]

    first_stage = activities[activities.index == activities.index.min()]
    # first_stage = activities[activities["start_date"] == activities["start_date"].min()]

    # Grand depart marker
    icon_ = BeautifyIcon(
        icon=settings.get_interactive_setting("depart_icon"),
        icon_shape=settings.get_interactive_setting("depart_icon_shape"),
        border_color=(
            "transparent"
            if settings.get_interactive_setting("depart_border_transparent")
            else settings.get_interactive_setting("depart_border_color")
        ),
        text_color=settings.get_interactive_setting("depart_symbol_color"),
        background_color=(
            "transparent"
            if settings.get_interactive_setting("depart_background_transparent")
            else settings.get_interactive_setting("depart_background_color")
        ),
        icon_size=[
            settings.get_interactive_setting("depart_icon_size"),
            settings.get_interactive_setting("depart_icon_size"),
        ],
        icon_anchor=(
            int(settings.get_interactive_setting("depart_icon_size")) / 2,
            int(settings.get_interactive_setting("depart_icon_size")) / 2,
        ),
        inner_icon_style=f"font-size:{settings.get_interactive_setting('depart_icon_inner_size')}px;",  # Adjust inner icon size
        id="grand_depart",
    )

    folium.Marker(
        location=first_stage["start_latlng"].iloc[0],
        icon=icon_,
        icon_size=10,
        zIndexOffset=1000,
        tooltip=first_stage["start_location"].iloc[0],
    ).add_to(grand_depart)

    return grand_depart
